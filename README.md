<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><pre><code class="language-bash"><span class="token"># AI Medical Appointment Scheduling Agent (RagaAI Case Study)</span><span>
</span>
<span></span><span class="token">!</span><span class="token">[</span><span>LangGraph</span><span class="token">]</span><span class="token">(</span><span>https://img.shields.io/badge/Orchestration-LangGraph-orange</span><span class="token">)</span><span class="token">!</span><span class="token">[</span><span>LangChain</span><span class="token">]</span><span class="token">(</span><span>https://img.shields.io/badge/Framework-LangChain-blue</span><span class="token">)</span><span class="token">!</span><span class="token">[</span><span>Python</span><span class="token">]</span><span class="token">(</span><span>https://img.shields.io/badge/Python-3.10+-blue?logo</span><span class="token">=</span><span>python</span><span class="token">)</span><span class="token">!</span><span class="token">[</span><span>Streamlit</span><span class="token">]</span><span class="token">(</span><span>https://img.shields.io/badge/UI-Streamlit-red</span><span class="token">)</span><span>
</span>
<span>This project is a fully functional AI-powered medical scheduling agent, built as a solution to the Data Science Intern </span><span class="token">case</span><span> study from RagaAI. It automates the entire patient booking process, from initial greeting to post-booking reminders, effectively addressing key operational inefficiencies </span><span class="token">in</span><span> medical practices.
</span>
<span></span><span class="token">## 🚀 Project Overview</span><span>
</span>
<span>The core business problem is the significant revenue loss </span><span class="token">(</span><span class="token">20</span><span>-50%</span><span class="token">)</span><span></span><span class="token">in</span><span> medical practices due to patient no-shows, scheduling errors, and administrative overhead. This AI agent tackles this by providing a seamless, automated, and intelligent scheduling experience.
</span>
The system is architected into two primary components:
<span></span><span class="token">1</span><span>.  **A Real-Time Conversational Agent:** Handles the interactive booking conversation with patients.
</span><span></span><span class="token">2</span><span>.  **An Asynchronous Reminder Manager:** Works </span><span class="token">in</span><span> the background to send automated, multi-step reminders to reduce no-shows.
</span>
<span></span><span class="token">## ✨ Core Features Implemented</span><span>
</span>
<span></span><span class="token">|</span><span> Feature                  </span><span class="token">|</span><span> Status </span><span class="token">|</span><span> Implementation Details                                                                                                                              </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> ------------------------ </span><span class="token">|</span><span> :----: </span><span class="token">|</span><span> --------------------------------------------------------------------------------------------------------------------------------------------------- </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> **Patient Greeting </span><span class="token">&</span><span> NLP**   </span><span class="token">|</span><span>   ✅   </span><span class="token">|</span><span> Greets </span><span class="token">users</span><span> and uses an LLM to extract Name, DOB, email, and phone from natural language.                                                          </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> **Patient Lookup**           </span><span class="token">|</span><span>   ✅   </span><span class="token">|</span><span> Integrates with a SQLite database </span><span class="token">(</span><span>simulating an EMR</span><span class="token">)</span><span> to identify new vs. returning patients.                                                     </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> **Smart Scheduling**         </span><span class="token">|</span><span>   ✅   </span><span class="token">|</span><span> Dynamically allocates appointment durations: **60 minutes** </span><span class="token">for</span><span> new patients and **30 minutes** </span><span class="token">for</span><span> returning patients.                               </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> **Calendar Integration**     </span><span class="token">|</span><span>   ✅   </span><span class="token">|</span><span> Finds and displays available slots from mock doctor schedules </span><span class="token">(</span><span>Excel files</span><span class="token">)</span><span>.                                                                      </span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span> **Insurance Collection**     </span><span class="token">|</span><span>   ✅   </span><span class="token">|</span><span> Securely captures and structures the patient</span><span class="token">'s insurance carrier and member ID during the booking flow.                                           |
</span><span class="token">| **Appointment Confirmation** |   ✅   | Books the appointment in the database, generates an admin-ready Excel export, and sends an email confirmation.                                    |
</span><span class="token">| **Form Distribution**        |   ✅   | Automatically attaches the "New Patient Intake Form.pdf" to the confirmation email sent upon successful booking.                                  |
</span><span class="token">| **3-Step Reminder System**   |   ✅   | A standalone script sends 3 waves of reminders (3-day, 24-hour, and 4-hour) with logic for checking form completion and visit confirmation. |
</span><span class="token">
</span><span class="token">## 🛠️ Technical Architecture
</span><span class="token">
</span><span class="token">This project uses a multi-agent orchestration pattern with LangGraph to create a robust, stateful conversational flow.
</span><span class="token">
</span><span class="token">**1. Conversational Agent (`agent.py`)**
</span><span class="token">
</span><span class="token">The agent is a State Graph that transitions between nodes based on the conversation'</span><span>s context.
</span>
```plaintext
<span></span><span class="token">(</span><span>START</span><span class="token">)</span><span> --</span><span class="token">></span><span></span><span class="token">[</span><span>decide_entry_point</span><span class="token">]</span><span> --</span><span class="token">></span><span></span><span class="token">|</span><span>new convo</span><span class="token">|</span><span> --</span><span class="token">></span><span></span><span class="token">[</span><span>greet_patient</span><span class="token">]</span><span>
</span><span></span><span class="token">|</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span>-</span><span class="token">></span><span></span><span class="token">|</span><span>user input</span><span class="token">|</span><span> -</span><span class="token">></span><span></span><span class="token">[</span><span>extract_patient_details</span><span class="token">]</span><span> -</span><span class="token">></span><span></span><span class="token">[</span><span>check_patient_record</span><span class="token">]</span><span>
</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span>----------------------------</span><span class="token">|</span><span>----------------------------</span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span></span><span class="token">(</span><span>new patient</span><span class="token">)</span><span></span><span class="token">|</span><span></span><span class="token">(</span><span>returning patient</span><span class="token">)</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">v</span><span></span><span class="token">v</span><span></span><span class="token">v</span><span>
</span><span></span><span class="token">[</span><span>request_missing_info</span><span class="token">]</span><span> -</span><span class="token">></span><span></span><span class="token">[</span><span>create_new_patient</span><span class="token">]</span><span></span><span class="token">[</span><span>find_slots_returning</span><span class="token">]</span><span>
</span><span></span><span class="token">|</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">|</span><span>----------------------------</span><span class="token">|</span><span>
</span><span></span><span class="token">v</span><span>
</span><span></span><span class="token">(</span><span>Displays Slots</span><span class="token">)</span><span>
</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">(</span><span>User Selects Slot</span><span class="token">)</span><span>
</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">v</span><span>
</span><span></span><span class="token">[</span><span>process_slot_selection</span><span class="token">]</span><span>
</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">(</span><span>User Provides Insurance</span><span class="token">)</span><span>
</span><span></span><span class="token">|</span><span>
</span><span></span><span class="token">v</span><span>
</span><span></span><span class="token">[</span><span>book_appointment</span><span class="token">]</span><span> --</span><span class="token">></span><span></span><span class="token">(</span><span>END</span><span class="token">)</span></code></pre></div></pre>

**2. Asynchronous Reminder Manager (reminder_manager.py)**

This is a separate, scheduled script that runs independently of the chat agent. It queries the database for upcoming appointments and progresses them through the reminder states.

Confirmed -> Reminder 1 Sent -> Reminder 2 Sent -> Reminder 3 Sent

## ⚙️ Tech Stack

* **Orchestration:** LangGraph
* **Core AI Framework:** LangChain
* **LLM:** phi3:mini (via Ollama)
* **Database:** SQLite
* **UI:** Streamlit
* **File Operations:** Pandas, Openpyxl
* **Environment Management:** Python venv

## 🗂️ Project Structure

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">text</span></div></div><pre><code class="language-text"><span>medical_ai_agent/
</span>├── data/
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
└── README.md               # You are here!</code></pre></div></pre>

## ⚡️ Setup and Installation (Terminal Only)

### 1. Clone the Repository

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span class="token"># Replace with your repository URL</span><span>
</span><span></span><span class="token">git</span><span> clone https://github.com/your-username/medical_ai_agent.git
</span><span></span><span class="token">cd</span><span> medical_ai_agent</span></code></pre></div></pre>

### 2. Set Up Virtual Environment

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span>python3 -m venv venv
</span><span></span><span class="token">source</span><span> venv/bin/activate</span></code></pre></div></pre>

### 3. Install Dependencies

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span>pip </span><span class="token">install</span><span> -r requirements.txt</span></code></pre></div></pre>

### 4. Configure Environment Variables

Create a .env file to store your email credentials for sending confirmations.

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span class="token">echo</span><span></span><span class="token">"EMAIL_USER=your_email@gmail.com"</span><span></span><span class="token">></span><span> .env
</span><span></span><span class="token">echo</span><span></span><span class="token">"EMAIL_PASS=your_gmail_app_password"</span><span></span><span class="token">>></span><span> .env</span></code></pre></div></pre>

***Note:** For Gmail, you must generate an "App Password" from your Google Account security settings.*

### 5. Initialize the Database

This script will create clinic.db, set up the necessary tables, and populate it with 50 synthetic patients.

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span>python setup_database.py</span></code></pre></div></pre>

## ▶️ How to Run the Application

### 1. Run the Conversational AI Agent

Launch the Streamlit web interface.

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span>streamlit run app.py</span></code></pre></div></pre>

Open your browser to the local URL provided by Streamlit (usually http://localhost:8501).

### 2. Run the Reminder System

To simulate the automated reminder system, run this script in a separate terminal. In a real-world scenario, this would be scheduled with a cron job.

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">bash</span></div></div><pre><code class="language-bash"><span class="token"># This will check for any appointments needing reminders and "send" them.</span><span>
</span>python reminder_manager.py</code></pre></div></pre>

EOF

<pre class="p-0 m-0 rounded-xl"><div class="rt-Box relative"><div class="rt-Flex rt-r-fd-column rt-r-py-1 rt-r-w absolute top-2 z-10 px-[14px]"><div class="rt-Flex rt-r-fd-row rt-r-ai-center rt-r-jc-space-between"><span data-accent-color="gray" class="rt-Text">text</span></div></div><br class="Apple-interchange-newline"/></div></pre>
