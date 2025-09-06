AI Medical Appointment Scheduling Agent (RagaAI Case Study)
OrchestrationFrameworkPythonUIThis project is a fully functional AI-powered medical scheduling agent, built as a solution to the Data Science Intern case study from RagaAI. It automates the entire patient booking process, from initial greeting to post-booking reminders, effectively addressing key operational inefficiencies in medical practices.

🚀 Project Overview
The core business problem is the significant revenue loss (20-50%) in medical practices due to patient no-shows, scheduling errors, and administrative overhead. This AI agent tackles this by providing a seamless, automated, and intelligent scheduling experience.

The system is architected into two primary components:

A Real-Time Conversational Agent: Handles the interactive booking conversation with patients.
An Asynchronous Reminder Manager: Works in the background to send automated, multi-step reminders to reduce no-shows.
✨ Core Features Implemented
Feature	Status	Implementation Details
Patient Greeting & NLP	✅	Greets users and uses an LLM to extract Name, DOB, email, and phone from natural language.
Patient Lookup	✅	Integrates with a SQLite database (simulating an EMR) to identify new vs. returning patients.
Smart Scheduling	✅	Dynamically allocates appointment durations: 60 minutes for new patients and 30 minutes for returning patients.
Calendar Integration	✅	Finds and displays available slots from mock doctor schedules (Excel files).
Insurance Collection	✅	Securely captures and structures the patient's insurance carrier and member ID during the booking flow.
Appointment Confirmation	✅	Books the appointment in the database, generates an admin-ready Excel export, and sends an email confirmation.
Form Distribution	✅	Automatically attaches the "New Patient Intake Form.pdf" to the confirmation email sent upon successful booking.
3-Step Reminder System	✅	A standalone script sends 3 waves of reminders (3-day, 24-hour, and 4-hour) with logic for checking form completion and visit confirmation.
🛠️ Technical Architecture
This project uses a multi-agent orchestration pattern with LangGraph to create a robust, stateful conversational flow.

1. Conversational Agent (agent.py)
The agent is a State Graph that transitions between nodes based on the conversation's context.

plaintext
(START) -->> [decide_entry_point] -->> |new convo| -->> [greet_patient]
   |
   |->> |user input| ->> [extract_patient_details] ->> [check_patient_record]
                                                           |
                      +------------------------------------+------------------------------------+
                      | (new patient)                      | (returning patient)                |
                      v                                    v                                    v
            [request_missing_info] ->> [create_new_patient]         [find_slots_returning]
                      |                                    |
                      +------------------------------------+
                                                           |
                                                           v
                                                  (Displays Slots)
                                                           |
                                                 (User Selects Slot)
                                                           |
                                                           v
                                             [process_slot_selection]
                                                           |
                                             (User Provides Insurance)
                                                           |
                                                           v
                                                  [book_appointment] -->> (END)
2. Asynchronous Reminder Manager (reminder_manager.py)
This is a separate, scheduled script that runs independently of the chat agent. It queries the database for upcoming appointments and progresses them through the reminder states:

Confirmed -> Reminder 1 Sent -> Reminder 2 Sent -> Reminder 3 Sent

⚙️ Tech Stack
Orchestration: LangGraph
Core AI Framework: LangChain
LLM: phi3:mini (via Ollama)
Database: SQLite
UI: Streamlit
File Operations: Pandas, Openpyxl
Environment Management: Python venv
🗂️ Project Structure
text
medical_ai_agent/
├── data/
│   └── clinic.db           # SQLite database for patient & appointment data
├── forms/
│   └── New Patient Intake Form.pdf # PDF attachment for confirmation emails
├── venv/
├── .env                    # Stores secret credentials (ignored by git)
├── app.py                  # Main Streamlit UI file, handles chat interface
├── agent.py                # Core application logic: LangGraph state machine
├── tools.py                # Business logic functions (LangChain tools)
├── reminder_manager.py     # Asynchronous script for sending reminders
├── setup_database.py       # Script to initialize the SQLite database
├── requirements.txt        # Python package dependencies
└── README.md               # You are here!
⚡️ Setup and Installation
1. Clone the Repository
bash
# Replace with your actual repository URL
git clone https://github.com/your-username/medical_ai_agent.git
cd medical_ai_agent
2. Set Up Virtual Environment
bash
python3 -m venv venv
source venv/bin/activate
Note: On Windows, the activation command is venv\Scripts\activate

3. Install Dependencies
bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file to store your email credentials for sending confirmations.

bash
echo "EMAIL_USER=your_email@gmail.com" > .env
echo "EMAIL_PASS=your_gmail_app_password" >> .env
Important: For Gmail, you must generate an "App Password" from your Google Account security settings. Your regular password will not work.

5. Initialize the Database
This script will create clinic.db, set up the necessary tables, and populate it with 50 synthetic patients.

bash
python setup_database.py
▶️ How to Run the Application
1. Run the Conversational AI Agent
Launch the Streamlit web interface.

bash
streamlit run app.py
Open your browser to the local URL provided by Streamlit (usually http://localhost:8501).

2. Run the Reminder System
To simulate the automated reminder system, run this script in a separate terminal. In a real-world scenario, this would be scheduled with a cron job.

bash
# This will check for any appointments needing reminders and "send" them.
python reminder_manager.py
