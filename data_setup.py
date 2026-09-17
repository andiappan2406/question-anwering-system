"""
Run this ONCE before starting the server.
It creates:
  1. data/students.db   -> a tiny SQLite database (structured data)
  2. data/documents.json -> sample FAQ/policy/course content (unstructured data)
"""

import sqlite3
import json
import os

os.makedirs("data", exist_ok=True)

# ---------- 1. Structured data (SQLite) ----------
conn = sqlite3.connect("data/students.db")
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS students")
c.execute("""
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    attendance_percentage REAL,
    gpa REAL,
    semester INTEGER
)
""")

sample_students = [
    ("S101", "Arun Kumar", 82.5, 8.2, 5),
    ("S102", "Divya Priya", 68.0, 7.5, 5),
    ("S103", "Karthik Raja", 91.0, 9.1, 5),
]
c.executemany("INSERT INTO students VALUES (?,?,?,?,?)", sample_students)
conn.commit()
conn.close()
print("[OK] Created data/students.db with sample records")

# ---------- 2. Unstructured data (documents) ----------
documents = [
    {
        "id": "policy_attendance_01",
        "source": "Attendance Policy",
        "text": "Students must maintain a minimum of 75 percent attendance in each subject to be eligible to write the semester examination. Students below 75 percent attendance will be debarred from the exam unless a valid medical certificate is submitted within 7 days."
    },
    {
        "id": "policy_exam_retake_01",
        "source": "Exam Retake Policy",
        "text": "Students who fail a semester exam are eligible for one retake or arrear attempt in the subsequent semester. A retake fee of Rs. 500 per subject applies. Students cannot retake a subject more than twice."
    },
    {
        "id": "faq_library_01",
        "source": "Library FAQ",
        "text": "The AMYPO library is open from 8:30 AM to 7:00 PM on weekdays and 9:00 AM to 1:00 PM on Saturdays. Students can borrow up to 3 books for 14 days using their student ID card."
    },
    {
        "id": "course_dbms_01",
        "source": "DBMS Course Content - Module 3",
        "text": "Module 3 of the Database Management Systems course covers Normalization, including First Normal Form, Second Normal Form, and Third Normal Form, along with functional dependencies and how they help eliminate data redundancy."
    },
    {
        "id": "faq_placement_01",
        "source": "Placement FAQ",
        "text": "Students become eligible for campus placements starting from the 6th semester, provided they have no standing arrears and maintain a minimum CGPA of 6.5."
    },
]

with open("data/documents.json", "w") as f:
    json.dump(documents, f, indent=2)
print("[OK] Created data/documents.json with sample FAQ/policy/course content")
