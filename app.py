import streamlit as st
import uuid
from collections import defaultdict
from langchain_core.messages import HumanMessage

from agent import agent_runnable
from tools import generate_admin_report

st.set_page_config(
    page_title="AI Medical Appointment Scheduling Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stChatMessage { border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
    [data-testid="chat-message-container-user"] { background-color: #262730; }
    [data-testid="chat-message-container-assistant"] { background-color: #1a1c24; }
    .stButton>button { border-radius: 8px; border: 1px solid #4F8BF9; background-color: transparent; color: #4F8BF9; transition: all 0.2s ease-in-out; }
    .stButton>button:hover { background-color: #4F8BF9; color: white; border-color: #4F8BF9; }
    .stButton>button:focus { box-shadow: 0 0 0 2px #4F8BF9; }
    [data-testid="stVerticalBlock"] .st-emotion-cache-16txtl3 { background-color: #1a1c24; border: 1px solid #262730; border-radius: 10px; padding: 1rem; }
    h1 { color: #4F8BF9; text-align: center; }
</style>
""", unsafe_allow_html=True)

def reset_conversation():
    """Resets the conversation state."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.agent_state = {}
    
    # **FIXED LINE** Provide an empty list for messages on the first run.
    initial_state = agent_runnable.invoke({"messages": []}, config={"configurable": {"thread_id": st.session_state.thread_id}})
    
    st.session_state.messages.extend(initial_state['messages'])
    st.session_state.agent_state = initial_state

def display_dashboard(state):
    """Displays the live status dashboard from the agent's state."""
    with st.container(border=True):
        st.markdown("### 🗓️ Booking Status")
        
        p_info = state.get("patient_info", {})
        b_info = state.get("booking_info", {})

        if state.get("final_confirmation"):
            progress_text = "**Step 4 of 4:** Confirmed"
        elif b_info.get("appointment_time"):
             progress_text = "**Step 3 of 4:** Insurance Details"
        elif b_info.get("slots"):
             progress_text = "**Step 2 of 4:** Select Slot"
        else:
            progress_text = "**Step 1 of 4:** Patient Info"

        st.caption(progress_text)
        st.markdown("---")
        st.markdown("**👤 Patient Details**")
        st.markdown(f"**Name:** `{p_info.get('full_name', '...')}`")
        st.markdown(f"**DoB:** `{p_info.get('date_of_birth', '...')}`")
        st.markdown(f"**Email:** `{p_info.get('email', '...')}`")
        st.markdown(f"**Phone:** `{p_info.get('phone_number', '...')}`")
        st.markdown("---")
        st.markdown("** Appointment Details**")
        st.markdown(f"**Doctor:** `{b_info.get('doctor_name', '...')}`")
        st.markdown(f"**Time:** `{b_info.get('appointment_time', '...')}`")
        st.markdown(f"**Duration:** `{str(b_info.get('duration', '...'))} mins`")

st.title("🩺 AI Medical Appointment Scheduling Agent")

if "thread_id" not in st.session_state:
    reset_conversation()

chat_col, dashboard_col = st.columns([2, 1])

with dashboard_col:
    display_dashboard(st.session_state.agent_state)

with chat_col:
    with st.sidebar:
        st.header("Admin Panel")
        if st.button("Generate Admin Report"):
            with st.spinner("Generating report..."):
                report_path = generate_admin_report()
                st.success(f"Report generated: `{report_path}`")
        st.header("Controls")
        if st.button("Start New Booking"):
            reset_conversation()
            st.rerun()

    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    def run_agent(messages):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.spinner("Thinking..."):
            final_state = agent_runnable.invoke({"messages": messages}, config)
        st.session_state.agent_state = final_state
        st.session_state.messages = final_state["messages"]
        st.rerun()

    slots = st.session_state.agent_state.get("booking_info", {}).get("slots", [])
    if slots:
        with st.chat_message("assistant"):
            st.markdown("Please select one of the available slots below:")
            grouped_slots = defaultdict(list)
            for slot in slots:
                doctor, slot_time = slot.split(" at ")
                grouped_slots[doctor].append((slot_time, slot))
            
            for doctor, times in grouped_slots.items():
                st.markdown(f"**{doctor}**")
                cols = st.columns(3)
                for i, (slot_time, full_slot) in enumerate(times):
                    if cols[i % 3].button(slot_time, key=full_slot):
                        user_message = HumanMessage(content=f"I'll take the slot: {full_slot}")
                        st.session_state.messages.append(user_message)
                        run_agent([user_message])

    if final_confirmation := st.session_state.agent_state.get("final_confirmation"):
        with st.chat_message("assistant"):
            st.success("Booking complete!", icon="✅")
            st.markdown(final_confirmation)
        if email_status := st.session_state.agent_state.get("email_status"):
            if email_status == "Sent":
                with st.chat_message("assistant"):
                    st.markdown("A confirmation email with your intake form is on its way. We look forward to seeing you!")
            else:
                with st.chat_message("assistant"):
                    st.warning(f"Note: I couldn't send a confirmation email due to an issue: {email_status}")
        st.session_state.agent_state["final_confirmation"] = None

    if prompt := st.chat_input("Your response..."):
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        run_agent([user_message])