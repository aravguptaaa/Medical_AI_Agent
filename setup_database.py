import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker for data generation
fake = Faker()

# --- Configuration ---
DB_FILE = "data/clinic.db"
NUM_PATIENTS = 50
NUM_DOCTORS = 3
DAYS_TO_SCHEDULE = 14 # Generate schedule for the next 14 days

def create_connection(db_file):
    """ Create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite version: {sqlite3.version}")
        print(f"Successfully connected to {db_file}")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create the necessary tables if they don't exist """
    try:
        cursor = conn.cursor()
        # Patients Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patients (
            PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
            FullName TEXT NOT NULL,
            DateOfBirth TEXT NOT NULL,
            Email TEXT,
            PhoneNumber TEXT
        );
        """)
        
        # Doctor Schedules Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DoctorSchedules (
            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            DoctorName TEXT NOT NULL,
            StartTime TEXT NOT NULL,
            EndTime TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Available' -- Available, Booked
        );
        """)

        # Appointments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Appointments (
            AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientID INTEGER,
            DoctorName TEXT NOT NULL,
            AppointmentTime TEXT NOT NULL,
            Duration INTEGER NOT NULL, -- in minutes (30 or 60)
            InsuranceCarrier TEXT,
            MemberID TEXT,
            Status TEXT NOT NULL, -- e.g., Confirmed, Forms Sent, Reminder 1 Sent
            FOREIGN KEY (PatientID) REFERENCES Patients (PatientID)
        );
        """)
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")


def generate_synthetic_data(conn):
    """ Generate and insert synthetic data into the tables """
    cursor = conn.cursor()
    
    # 1. Generate Patients
    patients = []
    for _ in range(NUM_PATIENTS):
        patients.append((
            fake.name(),
            fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d'),
            fake.email(),
            fake.phone_number()
        ))
    cursor.executemany("INSERT INTO Patients (FullName, DateOfBirth, Email, PhoneNumber) VALUES (?, ?, ?, ?)", patients)
    print(f"Inserted {len(patients)} synthetic patients.")

    # 2. Generate Doctor Schedules
    doctors = [f"Dr. {fake.last_name()}" for _ in range(NUM_DOCTORS)]
    schedules = []
    start_date = datetime.now().date()
    
    for day in range(DAYS_TO_SCHEDULE):
        current_date = start_date + timedelta(days=day)
        # Skip weekends
        if current_date.weekday() >= 5:
            continue
            
        for doctor in doctors:
            # Morning slots (9 AM to 12 PM)
            for hour in range(9, 12):
                schedules.append((doctor, f"{current_date} {hour:02d}:00", f"{current_date} {hour:02d}:30"))
                schedules.append((doctor, f"{current_date} {hour:02d}:30", f"{current_date} {hour+1:02d}:00"))
            # Afternoon slots (1 PM to 5 PM)
            for hour in range(13, 17):
                schedules.append((doctor, f"{current_date} {hour:02d}:00", f"{current_date} {hour:02d}:30"))
                schedules.append((doctor, f"{current_date} {hour:02d}:30", f"{current_date} {hour+1:02d}:00"))

    cursor.executemany("INSERT INTO DoctorSchedules (DoctorName, StartTime, EndTime) VALUES (?, ?, ?)", schedules)
    print(f"Inserted {len(schedules)} available slots for {NUM_DOCTORS} doctors.")

    conn.commit()

if __name__ == '__main__':
    conn = create_connection(DB_FILE)
    if conn:
        create_tables(conn)
        generate_synthetic_data(conn)
        conn.close()
        print("Database setup complete.")
