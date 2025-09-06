import os
import sqlite3
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.chat_models import ChatOllama
from pydantic import BaseModel, Field, model_validator
from typing import Any
from tools import (
    search_patient_tool,
    add_new_patient_tool,
    find_slots_tool,
    book_appointment_tool,
    send_confirmation_email_tool
)
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver

# --- 1. Define LLM and Pydantic Models for Extraction ---
llm = ChatOllama(model="phi3:mini", format="json", temperature=0)

class PatientDetails(BaseModel):
    full_name: Optional[str] = Field(default=None, description="The patient's full name.")
    date_of_birth: Optional[str] = Field(default=None, description="The patient's date of birth in YYYY-MM-DD format.")
    email: Optional[str] = Field(default=None, description="The patient's email address.")
    phone_number: Optional[str] = Field(default=None, description="The patient's phone number.")

    @model_validator(mode='before')
    @classmethod
    def sanitize_lists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for field, value in data.items():
                if isinstance(value, list):
                    data[field] = " ".join(map(str, value))
        return data

class InsuranceDetails(BaseModel):
    insurance_carrier: Optional[str] = Field(default=None, description="The patient's insurance provider.")
    member_id: Optional[str] = Field(default=None, description="The patient's insurance member ID.")

    @model_validator(mode='before')
    @classmethod
    def sanitize_lists(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for field, value in data.items():
                if isinstance(value, list):
                    data[field] = " ".join(map(str, value))
        return data

def get_llm_extractor(pydantic_model: Any) -> Any:
    parser = PydanticOutputParser(pydantic_object=pydantic_model)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert extraction algorithm. Only extract values from the text. Do not guess. Your output MUST be a JSON object that adheres to the provided schema below.\n\nSCHEMA:\n{format_instructions}"),
            ("human", "TEXT:\n{user_message}"),
        ]
    )
    return prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser

# --- 2. Define the State for the Graph ---
class GraphState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    patient_info: dict
    booking_info: dict
    is_new_patient: Optional[bool]
    final_confirmation: Optional[str]
    email_status: Optional[str]

# --- 3. Define the Nodes of the Graph ---
def greet_patient(state: GraphState):
    message = AIMessage(content="Hello! To book an appointment, please provide your **full name** and **date of birth** (YYYY-MM-DD). You can also include your email and phone number to speed things up.")
    return {"messages": [message]}

def extract_patient_details(state: GraphState):
    user_message = state["messages"][-1].content
    extractor = get_llm_extractor(PatientDetails)
    extracted_data = extractor.invoke({"user_message": user_message})
    current_patient_info = state.get("patient_info", {})
    current_patient_info.update(extracted_data.dict(exclude_unset=True, exclude_none=True))
    return {"patient_info": current_patient_info}

#
# =========================================================================================
# FIX #1: The validation logic is REMOVED from check_patient_record.
# This node now ONLY checks the database, assuming it has the data it needs.
# =========================================================================================
#
def check_patient_record(state: GraphState):
    patient_info = state["patient_info"]
    full_name, dob = patient_info.get("full_name"), patient_info.get("date_of_birth")
    
    search_result = search_patient_tool.invoke({"full_name": full_name, "date_of_birth": dob})
    if search_result["status"] == "Patient Not Found":
        message = AIMessage(content=f"I couldn't find a record for {full_name}. We'll need to create a new one.")
        return {"messages": [message], "is_new_patient": True}
    else:
        message = AIMessage(content=f"Welcome back, {search_result['full_name']}!")
        return {"messages": [message], "patient_info": search_result, "is_new_patient": False}

#
# =========================================================================================
# FIX #2: A NEW, simple node is created to handle the case of missing details.
# =========================================================================================
#
def ask_for_details(state: GraphState):
    message = AIMessage(content="I'm sorry, I need at least a **full name** and **date of birth** (YYYY-MM-DD) to proceed. Could you please provide them?")
    return {"messages": [message]}
    
def request_missing_info(state: GraphState):
    message = AIMessage(content="Could you also please provide your **email** and **phone number** to complete your profile?")
    return {"messages": [message]}

def create_new_patient_and_find_slots(state: GraphState):
    user_message = state["messages"][-1].content
    extractor = get_llm_extractor(PatientDetails)
    extracted_data = extractor.invoke({"user_message": user_message})
    patient_info = state["patient_info"]
    patient_info.update(extracted_data.dict(exclude_unset=True, exclude_none=True))
    new_patient = add_new_patient_tool.invoke(patient_info)
    messages = [AIMessage(content="Thank you, your profile is complete. New patient appointments are **60 minutes**."), AIMessage(content="Let me find available slots for you...")]
    slots = find_slots_tool.invoke({"duration": 60})
    booking_info = {'duration': 60, 'slots': slots.get('available_slots', [])}
    return {"patient_info": new_patient, "booking_info": booking_info, "messages": messages}
    
def find_slots_for_returning_patient(state: GraphState):
    messages = [AIMessage(content="Returning patient appointments are **30 minutes**."), AIMessage(content="Let me find available slots for you...")]
    slots = find_slots_tool.invoke({"duration": 30})
    booking_info = {'duration': 30, 'slots': slots.get('available_slots', [])}
    return {"booking_info": booking_info, "messages": messages}

def book_appointment_and_confirm(state: GraphState):
    user_message = state["messages"][-1].content
    extractor = get_llm_extractor(InsuranceDetails)
    insurance_data = extractor.invoke({"user_message": user_message})
    carrier, member_id = insurance_data.insurance_carrier or "Self-Pay", insurance_data.member_id or "N/A"
    booking_payload = {"patient_id": state['patient_info']['patient_id'], "doctor_name": state['booking_info']['doctor_name'], "appointment_time": state['booking_info']['appointment_time'], "duration": state['booking_info']['duration'], "insurance_carrier": carrier, "member_id": member_id}
    final_booking = book_appointment_tool.invoke(booking_payload)
    if final_booking.get("status") == "Booking Successful":
        email_result = send_confirmation_email_tool.invoke({"patient_id": state['patient_info']['patient_id'], "appointment_time": state['booking_info']['appointment_time']})
        confirmation_message = f"""### ✅ Appointment Confirmed!\nYour appointment is successfully booked.\n- **Patient:** {state['patient_info']['full_name']}\n- **With:** {state['booking_info']['doctor_name']}\n- **At:** {state['booking_info']['appointment_time']}"""
        return {"final_confirmation": confirmation_message, "email_status": email_result.get("email_status")}
    else:
        message = AIMessage(content="There was an issue confirming your booking. Please try again.")
        return {"messages": [message]}

def process_slot_selection(state: GraphState):
    chosen_slot = state["messages"][-1].content.replace("I'll take the slot: ", "")
    parts = chosen_slot.split(" at ")
    booking_info = state.get("booking_info", {})
    booking_info.update({'doctor_name': parts[0], 'appointment_time': parts[1]})
    message = AIMessage(content="Great! To finalize, could you please provide your **insurance carrier** and **member ID**? (If you are a self-payer, you can just say so).")
    return {"booking_info": booking_info, "messages": [message]}

# --- 4. Define Conditional Logic ---
def decide_after_check(state: GraphState):
    if state["is_new_patient"]:
        patient_info = state["patient_info"]
        if not patient_info.get("email") or not patient_info.get("phone_number"):
            return "request_missing_info"
        else:
            return "create_new_patient"
    else:
        return "find_slots_returning"

def decide_entry_point(state: GraphState):
    if not state.get("messages"):
        return "greet_patient"
    last_message = state["messages"][-1]
    if "I'll take the slot:" in last_message.content:
        return "process_slot_selection"
    if state.get("booking_info", {}).get("appointment_time"):
        return "book_appointment"
    if state.get("is_new_patient") is True and len(state["messages"]) > 3:
        return "create_new_patient"
    return "extract_patient_details"

#
# =========================================================================================
# FIX #3: A NEW conditional function to validate details after extraction.
# =========================================================================================
#
def details_are_sufficient(state: GraphState):
    patient_info = state["patient_info"]
    if not patient_info.get("full_name") or not patient_info.get("date_of_birth"):
        return "ask_for_details"
    else:
        return "proceed_to_check"

# --- 5. Build the Graph ---
workflow = StateGraph(GraphState)

workflow.add_node("greet_patient", greet_patient)
workflow.add_node("extract_patient_details", extract_patient_details)
workflow.add_node("check_patient_record", check_patient_record)
workflow.add_node("ask_for_details", ask_for_details) # Add the new node
workflow.add_node("request_missing_info", request_missing_info)
workflow.add_node("create_new_patient", create_new_patient_and_find_slots)
workflow.add_node("find_slots_returning", find_slots_for_returning_patient)
workflow.add_node("process_slot_selection", process_slot_selection)
workflow.add_node("book_appointment", book_appointment_and_confirm)

workflow.add_conditional_edges(START, decide_entry_point, {
    "greet_patient": "greet_patient",
    "process_slot_selection": "process_slot_selection",
    "create_new_patient": "create_new_patient",
    "extract_patient_details": "extract_patient_details",
    "book_appointment": "book_appointment",
})

workflow.add_edge("greet_patient", END) 
workflow.add_edge("ask_for_details", END) # The new failure path stops here.

#
# =========================================================================================
# FIX #4: The graph is re-wired to use the new validation step.
# =========================================================================================
#
workflow.add_conditional_edges(
    "extract_patient_details",
    details_are_sufficient,
    {
        "ask_for_details": "ask_for_details",
        "proceed_to_check": "check_patient_record",
    }
)

workflow.add_conditional_edges("check_patient_record", decide_after_check, {
    "request_missing_info": "request_missing_info",
    "create_new_patient": "create_new_patient",
    "find_slots_returning": "find_slots_returning",
})

workflow.add_edge("request_missing_info", END) 
workflow.add_edge("create_new_patient", END) 
workflow.add_edge("find_slots_returning", END) 
workflow.add_edge("process_slot_selection", END) 
workflow.add_edge("book_appointment", END)

conn = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(conn=conn)
agent_runnable = workflow.compile(checkpointer=memory)