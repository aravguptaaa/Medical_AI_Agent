# tools.py - COMPLETE AND UPDATED FILE

# --- All necessary imports ---
import sqlite3
import pandas as pd
from datetime import datetime
import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from langchain_core.tools import tool

# --- Load environment variables from .env file ---
load_dotenv()

# --- Constants ---
DB_FILE = "data/clinic.db"
PDF_FORM_PATH = "forms/New Patient Intake Form.pdf"


# --- Tools Updated for New UI ---

@tool
def search_patient_tool(full_name: str, date_of_birth: str) -> dict:
    """
    Searches for a patient and returns their full details to populate the dashboard.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Select all relevant fields needed by the app
        cursor.execute("SELECT PatientID, FullName, DateOfBirth, Email, PhoneNumber FROM Patients WHERE FullName LIKE ? AND DateOfBirth = ?", (f"%{full_name}%", date_of_birth))
        patient = cursor.fetchone()
        if patient:
            # Return a full dictionary that matches the app's expectations
            return {
                "status": "Patient Found",
                "patient_id": patient[0],
                "full_name": patient[1],
                "date_of_birth": patient[2],
                "email": patient[3],
                "phone_number": patient[4]
            }
    return {"status": "Patient Not Found"}

@tool
def add_new_patient_tool(full_name: str, date_of_birth: str, email: str, phone_number: str) -> dict:
    """
    Adds a new patient to the database and returns their full record for the dashboard.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Patients (FullName, DateOfBirth, Email, PhoneNumber) VALUES (?, ?, ?, ?)", (full_name, date_of_birth, email, phone_number))
        conn.commit()
        new_patient_id = cursor.lastrowid
    # Return the complete patient record, which the app now needs
    return {
        "status": "New Patient Added",
        "patient_id": new_patient_id,
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "email": email,
        "phone_number": phone_number
    }

@tool
def find_slots_tool(duration: int) -> dict:
    """Tool to find available appointment slots. Duration is 30 for returning patients, 60 for new patients."""
    try:
        limit = 10 if duration == 30 else 5
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DoctorName, StartTime FROM DoctorSchedules WHERE Status = 'Available' AND datetime(StartTime) > datetime('now') ORDER BY StartTime LIMIT ?", (limit,))
            slots = cursor.fetchall()
            if not slots:
                return {"status": "No slots available in the near future."}
            # Format slots for display
            formatted_slots = [f"{s[0]} at {datetime.strptime(s[1], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %I:%M %p')}" for s in slots]
        return {"available_slots": formatted_slots}
    except sqlite3.Error as e:
        return {"status": f"Error: Could not access calendar: {e}"}

@tool
def book_appointment_tool(patient_id: int, doctor_name: str, appointment_time: str, duration: int, insurance_carrier: str, member_id: str) -> dict:
    """Tool to book an appointment for a patient using their ID, chosen doctor, time, insurance, and member ID."""
    time_db_format = datetime.strptime(appointment_time, '%Y-%m-%d %I:%M %p').strftime('%Y-%m-%d %H:%M')
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Appointments (PatientID, DoctorName, AppointmentTime, Duration, InsuranceCarrier, MemberID, Status) VALUES (?, ?, ?, ?, ?, ?, 'Confirmed')", (patient_id, doctor_name, time_db_format, duration, insurance_carrier, member_id))
        cursor.execute("UPDATE DoctorSchedules SET Status = 'Booked' WHERE DoctorName = ? AND StartTime LIKE ?", (doctor_name, f"{time_db_format}%"))
        conn.commit()
    return {"status": "Booking Successful"}

@tool
def send_confirmation_email_tool(patient_id: int, appointment_time: str) -> dict:
    """Sends a REAL confirmation email to the patient with their intake form."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT FullName, Email FROM Patients WHERE PatientID = ?", (patient_id,))
            patient_info = cursor.fetchone()

        if not (patient_info and patient_info[1]):
            return {"email_status": "Failed: No email on file"}

        patient_name, patient_email = patient_info
        sender_email = os.getenv("EMAIL_HOST_USER")
        password = os.getenv("EMAIL_HOST_PASSWORD")

        if not sender_email or not password:
            print("ERROR: Email credentials not found in .env file.")
            return {"status": "Error", "message": "Email server not configured."}

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = patient_email
        msg['Subject'] = f"Appointment Confirmed: {appointment_time}"
        body = f"Dear {patient_name},\n\nThis confirms your appointment for {appointment_time}.\nPlease find your intake form attached.\n\nThank you,\nAura Health"
        msg.attach(MIMEText(body, 'plain'))

        with open(PDF_FORM_PATH, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(PDF_FORM_PATH)}")
        msg.attach(part)

        with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)

        print(f"Confirmation email successfully sent to {patient_email}")
        return {"email_status": "Sent"}

    except Exception as e:
        print(f"FAILED TO SEND EMAIL: {e}")
        return {"email_status": f"Failed: {e}"}

# --- Admin Helper Function (Not an LLM tool) ---
def generate_admin_report():
    """Generates an Excel report of all appointments."""
    with sqlite3.connect(DB_FILE) as conn:
        query = "SELECT a.AppointmentID, p.FullName, a.DoctorName, a.AppointmentTime FROM Appointments a JOIN Patients p ON a.PatientID = p.PatientID;"
        df = pd.read_sql_query(query, conn)
        report_path = "admin_report.xlsx"
        df.to_excel(report_path, index=False)
        return report_path
