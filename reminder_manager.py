# reminder_manager.py

import sqlite3
from datetime import datetime, timedelta

DB_FILE = "data/clinic.db"

# NOTE: This script assumes you've added a 'FormsFilled' column to your 'Appointments' table.
# You can add it with the following SQL command:
# ALTER TABLE Appointments ADD COLUMN FormsFilled INTEGER DEFAULT 0;

def handle_first_reminders(cursor):
    """
    Sends the initial reminder for appointments 1-3 days away.
    Trigger: Status is 'Confirmed'.
    Action: Sends a simple reminder and updates status to 'Reminder 1 Sent'.
    """
    print("\n[1] Checking for initial reminders (1-3 days out)...")
    now = datetime.now()
    one_day_from_now = now + timedelta(days=1)
    three_days_from_now = now + timedelta(days=3)

    cursor.execute("""
        SELECT a.AppointmentID, p.FullName, p.PhoneNumber, p.Email, a.AppointmentTime
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        WHERE a.Status = 'Confirmed' AND a.AppointmentTime BETWEEN ? AND ?
    """, (one_day_from_now, three_days_from_now))
    
    appointments = cursor.fetchall()
    if not appointments:
        print("   -> No appointments need a first reminder.")
        return 0

    for appt_id, name, phone, email, time_str in appointments:
        print(f"   -> Processing 1st reminder for {name} at {time_str}")
        # SIMULATE SENDING SMS/EMAIL
        print(f"      - SIMULATING SMS to {phone}: Hi {name}, this is a friendly reminder for your appointment on {time_str}.")
        print(f"      - SIMULATING EMAIL to {email}: Subject: Appointment Reminder. Body: ...")
        
        cursor.execute("UPDATE Appointments SET Status = 'Reminder 1 Sent' WHERE AppointmentID = ?", (appt_id,))
    return len(appointments)

def handle_second_reminders(cursor):
    """
    Sends the 24-hour reminder with action items.
    Trigger: Status is 'Reminder 1 Sent' and appointment is within 24 hours.
    Action: Checks form status, asks for confirmation, and updates status to 'Reminder 2 Sent'.
    """
    print("\n[2] Checking for second reminders (< 24 hours out)...")
    now = datetime.now()
    one_day_from_now = now + timedelta(days=1)

    cursor.execute("""
        SELECT a.AppointmentID, p.FullName, p.PhoneNumber, p.Email, a.AppointmentTime, a.FormsFilled
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        WHERE a.Status = 'Reminder 1 Sent' AND a.AppointmentTime <= ?
    """, (one_day_from_now,))

    appointments = cursor.fetchall()
    if not appointments:
        print("   -> No appointments need a second reminder.")
        return 0

    for appt_id, name, phone, email, time_str, forms_filled in appointments:
        print(f"   -> Processing 2nd reminder for {name} at {time_str}")
        
        # Action 1: Check if forms are filled
        if forms_filled:
            form_message = "We see you've already completed your intake forms - thank you!"
        else:
            form_message = "Please remember to fill out your patient intake forms sent to your email to ensure a quick check-in."

        # Action 2: Ask for confirmation
        confirmation_prompt = "Please reply YES to confirm your visit, or call us to reschedule."

        # SIMULATE SENDING SMS/EMAIL
        full_message = f"Hi {name}, your appointment is tomorrow at {time_str}. {form_message} {confirmation_prompt}"
        print(f"      - SIMULATING SMS to {phone}: {full_message}")
        print(f"      - SIMULATING EMAIL to {email}: Subject: Action Required: Confirm Your Appointment Tomorrow. Body: {full_message}")

        cursor.execute("UPDATE Appointments SET Status = 'Reminder 2 Sent' WHERE AppointmentID = ?", (appt_id,))
    return len(appointments)

def handle_third_reminders(cursor):
    """
    Sends the final reminder a few hours before the appointment.
    Trigger: Status is 'Reminder 2 Sent' and appointment is within 4 hours.
    Action: Sends a final "see you soon" message and updates status to 'Reminder 3 Sent'.
    """
    print("\n[3] Checking for final reminders (< 4 hours out)...")
    now = datetime.now()
    four_hours_from_now = now + timedelta(hours=4)

    cursor.execute("""
        SELECT a.AppointmentID, p.FullName, p.PhoneNumber, p.Email, a.AppointmentTime, a.FormsFilled
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        WHERE a.Status = 'Reminder 2 Sent' AND a.AppointmentTime BETWEEN ? AND ?
    """, (now, four_hours_from_now))
    
    appointments = cursor.fetchall()
    if not appointments:
        print("   -> No appointments need a final reminder.")
        return 0
        
    for appt_id, name, phone, email, time_str, forms_filled in appointments:
        print(f"   -> Processing 3rd (final) reminder for {name} at {time_str}")

        if forms_filled:
            form_message = "" # Don't bother them if they've already done it
        else:
            form_message = "PS: To speed up your check-in, please complete your intake forms before you arrive."
        
        full_message = f"Hi {name}, we look forward to seeing you for your appointment in a few hours at {time_str}. {form_message}"
        
        # SIMULATE SENDING SMS/EMAIL
        print(f"      - SIMULATING SMS to {phone}: {full_message}")
        print(f"      - SIMULATING EMAIL to {email}: Subject: See You Soon! Your Appointment is Today. Body: {full_message}")
        
        cursor.execute("UPDATE Appointments SET Status = 'Reminder 3 Sent' WHERE AppointmentID = ?", (appt_id,))
    return len(appointments)

def send_reminders():
    """
    Main function to find appointments needing reminders, simulate sending them,
    and update their status in the database.
    """
    print(f"--- Running Reminder Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    reminders_sent_count = 0
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        reminders_sent_count += handle_first_reminders(cursor)
        reminders_sent_count += handle_second_reminders(cursor)
        reminders_sent_count += handle_third_reminders(cursor)

        conn.commit()

        if reminders_sent_count == 0:
            print("\nConclusion: No reminders were sent in this run.")
        else:
            print(f"\nConclusion: Successfully processed and sent {reminders_sent_count} reminder(s).")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # To test this, you might need to manually set an appointment in your DB
    # to be in the near future with the status 'Confirmed'.
    send_reminders()
