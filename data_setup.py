"""
Data Setup Script for AMYPO Institute of Technology & Science.
Creates:
  1. data/students.db   -> SQLite database with comprehensive Students, Staff, and Courses tables.
  2. data/documents.json -> Curated, highly realistic college knowledge base (policies, facilities, academics, placements, etc.)
"""

import sqlite3
import json
import os

os.makedirs("data", exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. Structured Data (SQLite)
# ══════════════════════════════════════════════════════════════════════════════
conn = sqlite3.connect("data/students.db")
c = conn.cursor()

# ------------------------------------------------------------------------------
# Students Table
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS students")
c.execute("""
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INTEGER NOT NULL,
    section TEXT NOT NULL,
    attendance_percentage REAL NOT NULL,
    gpa REAL NOT NULL,
    fees_status TEXT NOT NULL,
    pending_dues INTEGER NOT NULL,
    email TEXT NOT NULL,
    mentor TEXT NOT NULL,
    hostel_details TEXT NOT NULL
)
""")

# Realistic student records
base_students = [
    {
        "id_num": "101",
        "name": "Arun Kumar",
        "department": "Computer Science & Engineering",
        "semester": 5,
        "section": "A",
        "attendance": 84.5,
        "gpa": 8.40,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "arun.kumar@amypo.edu.in",
        "mentor": "Dr. Rajesh Kumar (HoD CSE)",
        "hostel": "Cauvery Hostel, Room B-204",
    },
    {
        "id_num": "102",
        "name": "Divya Priya",
        "department": "Computer Science & Engineering",
        "semester": 5,
        "section": "A",
        "attendance": 68.0,
        "gpa": 7.50,
        "fees_status": "Pending: Rs. 15,000 for Semester 5",
        "pending_dues": 15000,
        "email": "divya.priya@amypo.edu.in",
        "mentor": "Prof. Anitha Raman (CSE)",
        "hostel": "Ganga Hostel, Room A-108",
    },
    {
        "id_num": "103",
        "name": "Karthik Raja",
        "department": "Computer Science & Engineering",
        "semester": 5,
        "section": "B",
        "attendance": 92.0,
        "gpa": 9.25,
        "fees_status": "Paid in full (Merit Scholarship 50% recipient)",
        "pending_dues": 0,
        "email": "karthik.raja@amypo.edu.in",
        "mentor": "Dr. Rajesh Kumar (HoD CSE)",
        "hostel": "Day Scholar (Bus Route 7 - Anna Nagar)",
    },
    {
        "id_num": "104",
        "name": "Ananya Iyer",
        "department": "Electronics & Communication Engineering",
        "semester": 5,
        "section": "A",
        "attendance": 89.0,
        "gpa": 8.85,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "ananya.iyer@amypo.edu.in",
        "mentor": "Dr. Meenakshi Sundaram (HoD ECE)",
        "hostel": "Yamuna Hostel, Room C-312",
    },
    {
        "id_num": "105",
        "name": "Rohan Deshmukh",
        "department": "Mechanical Engineering",
        "semester": 5,
        "section": "A",
        "attendance": 76.5,
        "gpa": 7.80,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "rohan.deshmukh@amypo.edu.in",
        "mentor": "Prof. Suresh Babu (HoD Mech)",
        "hostel": "Krishna Hostel, Room D-105",
    },
    {
        "id_num": "106",
        "name": "Sneha Patel",
        "department": "Information Technology",
        "semester": 3,
        "section": "A",
        "attendance": 94.2,
        "gpa": 9.40,
        "fees_status": "Paid in full (Merit Scholarship 50% recipient)",
        "pending_dues": 0,
        "email": "sneha.patel@amypo.edu.in",
        "mentor": "Dr. Harish Natarajan (HoD IT)",
        "hostel": "Ganga Hostel, Room A-215",
    },
    {
        "id_num": "107",
        "name": "Vikramaditya Rao",
        "department": "Artificial Intelligence & Data Science",
        "semester": 3,
        "section": "A",
        "attendance": 73.5,
        "gpa": 8.10,
        "fees_status": "Pending: Rs. 25,000 for Semester 3",
        "pending_dues": 25000,
        "email": "vikram.rao@amypo.edu.in",
        "mentor": "Prof. Pooja Nair (AI & DS)",
        "hostel": "Cauvery Hostel, Room B-110",
    },
    {
        "id_num": "108",
        "name": "Mohammed Farhan",
        "department": "Computer Science & Engineering",
        "semester": 7,
        "section": "A",
        "attendance": 85.0,
        "gpa": 8.70,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "m.farhan@amypo.edu.in",
        "mentor": "Dr. Rajesh Kumar (HoD CSE)",
        "hostel": "Day Scholar (Metro Pass - Guindy)",
    },
    {
        "id_num": "109",
        "name": "Kavya Sundaram",
        "department": "Electronics & Communication Engineering",
        "semester": 7,
        "section": "B",
        "attendance": 93.0,
        "gpa": 9.55,
        "fees_status": "Paid in full (Gold Medalist Track)",
        "pending_dues": 0,
        "email": "kavya.sundaram@amypo.edu.in",
        "mentor": "Dr. Meenakshi Sundaram (HoD ECE)",
        "hostel": "Yamuna Hostel, Room C-102",
    },
    {
        "id_num": "110",
        "name": "Siddharth Menon",
        "department": "Mechanical Engineering",
        "semester": 7,
        "section": "A",
        "attendance": 71.0,
        "gpa": 7.20,
        "fees_status": "Pending: Rs. 10,000 for Semester 7",
        "pending_dues": 10000,
        "email": "siddharth.m@amypo.edu.in",
        "mentor": "Prof. Suresh Babu (HoD Mech)",
        "hostel": "Krishna Hostel, Room D-208",
    },
    {
        "id_num": "111",
        "name": "Rhea Sengupta",
        "department": "Information Technology",
        "semester": 5,
        "section": "B",
        "attendance": 81.0,
        "gpa": 8.30,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "rhea.sengupta@amypo.edu.in",
        "mentor": "Dr. Harish Natarajan (HoD IT)",
        "hostel": "Ganga Hostel, Room A-304",
    },
    {
        "id_num": "112",
        "name": "Aditya Varma",
        "department": "Artificial Intelligence & Data Science",
        "semester": 5,
        "section": "A",
        "attendance": 88.0,
        "gpa": 8.95,
        "fees_status": "Paid in full (No outstanding dues)",
        "pending_dues": 0,
        "email": "aditya.varma@amypo.edu.in",
        "mentor": "Prof. Pooja Nair (AI & DS)",
        "hostel": "Day Scholar (Private Vehicle)",
    },
]

student_rows = []
for s in base_students:
    # Support both U-prefix (e.g. U101 - default in UI) and S-prefix (e.g. S101)
    for prefix in ["U", "S"]:
        student_rows.append((
            f"{prefix}{s['id_num']}",
            s["name"],
            s["department"],
            s["semester"],
            s["section"],
            s["attendance"],
            s["gpa"],
            s["fees_status"],
            s["pending_dues"],
            s["email"],
            s["mentor"],
            s["hostel"],
        ))

c.executemany(
    "INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
    student_rows,
)

# ------------------------------------------------------------------------------
# Staff / Faculty Table
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS staff")
c.execute("""
CREATE TABLE staff (
    staff_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT NOT NULL,
    office TEXT NOT NULL,
    specialization TEXT NOT NULL
)
""")

sample_staff = [
    (
        "T101",
        "Dr. Rajesh Kumar",
        "Computer Science & Engineering",
        "Professor & Head of Department (HoD)",
        "rajesh.cse@amypo.edu.in",
        "Tech Block-1, Room 301",
        "Distributed Systems, Cloud Computing & Relational DBs",
    ),
    (
        "T102",
        "Prof. Anitha Raman",
        "Computer Science & Engineering",
        "Assistant Professor & Year Coordinator",
        "anitha.cse@amypo.edu.in",
        "Tech Block-1, Room 305",
        "Database Management Systems & Big Data Analytics",
    ),
    (
        "T103",
        "Dr. Meenakshi Sundaram",
        "Electronics & Communication Engineering",
        "Professor & Head of Department (HoD)",
        "meenakshi.ece@amypo.edu.in",
        "VLSI Block, Room 201",
        "VLSI Architectures & Embedded IoT Systems",
    ),
    (
        "T104",
        "Prof. Suresh Babu",
        "Mechanical Engineering",
        "Associate Professor & Head of Department (HoD)",
        "suresh.mech@amypo.edu.in",
        "Workshop Block, Room 101",
        "Robotics, CAD/CAM & Industrial Automation",
    ),
    (
        "T105",
        "Dr. Vandana Hegde",
        "Academic Affairs",
        "Dean of Academics & Professor",
        "dean.academics@amypo.edu.in",
        "Admin Block, Room 102",
        "Curriculum Design & Software Quality Assurance",
    ),
    (
        "T106",
        "Dr. K. Radhakrishnan",
        "College Administration",
        "Principal & Director",
        "principal@amypo.edu.in",
        "Admin Block, Room 101",
        "Nanotechnology & Engineering Administration",
    ),
    (
        "T107",
        "Prof. Ramesh Varma",
        "Training & Placement Cell",
        "Placement Director & Associate Professor",
        "placements@amypo.edu.in",
        "Career Center, 2nd Floor",
        "Corporate Relations, Aptitude & Career Mentorship",
    ),
    (
        "T108",
        "Dr. Harish Natarajan",
        "Information Technology",
        "Associate Professor & Head of Department (HoD)",
        "harish.it@amypo.edu.in",
        "Tech Block-2, Room 204",
        "Cybersecurity, Cryptography & Network Protocols",
    ),
    (
        "T109",
        "Prof. Pooja Nair",
        "Artificial Intelligence & Data Science",
        "Assistant Professor",
        "pooja.aids@amypo.edu.in",
        "Tech Block-2, Room 310",
        "Deep Learning, Natural Language Processing & Computer Vision",
    ),
    (
        "T110",
        "Col. S. Vijayaraghavan",
        "Student Welfare & Hostels",
        "Chief Warden & Student Welfare Officer",
        "chiefwarden@amypo.edu.in",
        "Hostel Central Office",
        "Student Safety, Residential Life & Campus Discipline",
    ),
    (
        "staff_fac_4402",
        "Dr. Rajesh Kumar",
        "Computer Science & Engineering",
        "Professor & Head of Department (HoD)",
        "rajesh.cse@amypo.edu.in",
        "Tech Block-1, Room 301",
        "Distributed Systems, Cloud Computing & Relational DBs",
    ),
]
c.executemany("INSERT INTO staff VALUES (?,?,?,?,?,?,?)", sample_staff)

# ------------------------------------------------------------------------------
# Courses Table
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS courses")
c.execute("""
CREATE TABLE courses (
    course_code TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INTEGER NOT NULL,
    credits INTEGER NOT NULL,
    instructor TEXT NOT NULL
)
""")

sample_courses = [
    ("CS501", "Database Management Systems", "Computer Science & Engineering", 5, 4, "Dr. Rajesh Kumar"),
    ("CS502", "Operating Systems & Systems Programming", "Computer Science & Engineering", 5, 4, "Prof. Anitha Raman"),
    ("CS503", "Design and Analysis of Algorithms", "Computer Science & Engineering", 5, 4, "Dr. Harish Natarajan"),
    ("CS504", "Computer Networks & Security", "Computer Science & Engineering", 5, 3, "Prof. Pooja Nair"),
    ("HS101", "Tamil Heritage & Scientific Tamil", "Humanities & Sciences", 5, 2, "Dr. S. Swaminathan"),
    ("CS508", "DBMS & Networks Laboratory", "Computer Science & Engineering", 5, 2, "Prof. Anitha Raman"),
    ("EC501", "Digital Signal Processing", "Electronics & Communication Engineering", 5, 4, "Dr. Meenakshi Sundaram"),
    ("EC502", "Microprocessors and Microcontrollers", "Electronics & Communication Engineering", 5, 4, "Prof. K. Venkatesh"),
    ("ME501", "Thermal Engineering & Heat Transfer", "Mechanical Engineering", 5, 4, "Prof. Suresh Babu"),
    ("ME502", "Design of Machine Elements", "Mechanical Engineering", 5, 4, "Dr. N. Balaji"),
    ("AI301", "Foundations of Artificial Intelligence & Machine Learning", "Artificial Intelligence & Data Science", 3, 4, "Prof. Pooja Nair"),
    ("IT301", "Data Structures & Object-Oriented Programming", "Information Technology", 3, 4, "Dr. Harish Natarajan"),
]
c.executemany("INSERT INTO courses VALUES (?,?,?,?,?,?)", sample_courses)

# ------------------------------------------------------------------------------
# Student Course Attendance Table (Detailed subject-wise breakdown)
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS student_course_attendance")
c.execute("""
CREATE TABLE student_course_attendance (
    student_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    attendance_percentage REAL NOT NULL,
    classes_attended INTEGER NOT NULL,
    total_classes INTEGER NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (student_id, course_code)
)
""")

# Build realistic subject attendance for each student
sample_attendance = []
cse_subjects = [
    ("CS501", "Database Management Systems", 45, 0.90),
    ("CS502", "Operating Systems & Systems Programming", 45, 0.85),
    ("CS503", "Design and Analysis of Algorithms", 40, 0.82),
    ("CS504", "Computer Networks & Security", 40, 0.80),
    ("HS101", "Tamil Heritage & Scientific Tamil", 30, 0.92),
    ("CS508", "DBMS & Networks Laboratory", 25, 0.96),
]

for s in student_rows:
    sid = s[0]
    overall_att = s[5]
    for code, name, total_cls, mult in cse_subjects:
        # Scale individual attendance around student's overall attendance
        subject_att = round(min(100.0, max(55.0, overall_att * mult / 0.88)), 1)
        attended = int(round(total_cls * (subject_att / 100.0)))
        status = "Eligible" if subject_att >= 75.0 else ("Condonation Needed" if subject_att >= 65.0 else "Debarred")
        sample_attendance.append((sid, code, name, subject_att, attended, total_cls, status))

c.executemany("INSERT INTO student_course_attendance VALUES (?,?,?,?,?,?,?)", sample_attendance)

# ------------------------------------------------------------------------------
# Exam Schedule Table
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS exam_schedule")
c.execute("""
CREATE TABLE exam_schedule (
    course_code TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    exam_time TEXT NOT NULL,
    venue TEXT NOT NULL,
    session TEXT NOT NULL
)
""")

sample_exams = [
    ("HS101", "Tamil Heritage & Scientific Tamil", "2026-11-24", "09:30 AM - 12:30 PM", "Main Exam Block Rooms A-201 to A-208", "Forenoon"),
    ("CS501", "Database Management Systems", "2026-11-27", "09:30 AM - 12:30 PM", "Tech Block-1 Hall 101-105", "Forenoon"),
    ("CS502", "Operating Systems & Systems Programming", "2026-11-30", "09:30 AM - 12:30 PM", "Tech Block-1 Hall 101-105", "Forenoon"),
    ("CS503", "Design and Analysis of Algorithms", "2026-12-03", "09:30 AM - 12:30 PM", "Tech Block-1 Hall 101-105", "Forenoon"),
    ("CS504", "Computer Networks & Security", "2026-12-07", "09:30 AM - 12:30 PM", "Tech Block-1 Hall 101-105", "Forenoon"),
    ("EC501", "Digital Signal Processing", "2026-11-25", "09:30 AM - 12:30 PM", "VLSI Block Exam Hall", "Forenoon"),
    ("ME501", "Thermal Engineering & Heat Transfer", "2026-11-26", "09:30 AM - 12:30 PM", "Workshop Block Exam Hall", "Forenoon"),
]
c.executemany("INSERT INTO exam_schedule VALUES (?,?,?,?,?,?)", sample_exams)

# ------------------------------------------------------------------------------
# Company Openings Table (Placement Job Roles & Requirements)
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS company_openings")
c.execute("""
CREATE TABLE company_openings (
    opening_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    role_title TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    preferred_skills TEXT NOT NULL,
    min_cgpa REAL NOT NULL,
    min_attendance REAL NOT NULL,
    eligible_departments TEXT NOT NULL,
    ctc TEXT NOT NULL,
    location TEXT NOT NULL,
    positions_open INTEGER NOT NULL,
    deadline TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

sample_openings = [
    (
        "OPN-GOOG-01",
        "Google",
        "Backend Software Engineer (SDE-1)",
        json.dumps(["Python", "Go", "Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design"]),
        json.dumps(["Kubernetes", "gRPC", "Redis", "C++"]),
        8.5,
        75.0,
        json.dumps(["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science"]),
        "24 LPA",
        "Bangalore / Hyderabad",
        6,
        "2026-11-20",
        "Build scalable, high-throughput distributed systems, cloud microservices, and high-performance backend pipelines."
    ),
    (
        "OPN-MSFT-02",
        "Microsoft",
        "Data Scientist / Applied AI Engineer",
        json.dumps(["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "SQL", "Statistics"]),
        json.dumps(["Transformers", "Vector Databases", "LangChain", "FastAPI"]),
        8.0,
        75.0,
        json.dumps(["Artificial Intelligence & Data Science", "Computer Science & Engineering", "Information Technology"]),
        "21 LPA",
        "Hyderabad / Bangalore",
        5,
        "2026-11-22",
        "Design production ML pipelines, fine-tune transformer models, and deploy intelligent AI capabilities into core cloud products."
    ),
    (
        "OPN-AMZN-03",
        "Amazon",
        "Cloud Solutions Architect / DevOps Engineer",
        json.dumps(["AWS", "Linux", "Docker", "Kubernetes", "Python", "Networking", "CI/CD"]),
        json.dumps(["Terraform", "Ansible", "Prometheus", "Bash Scripting"]),
        7.5,
        75.0,
        json.dumps(["Computer Science & Engineering", "Information Technology", "Electronics & Communication Engineering"]),
        "18 LPA",
        "Chennai / Hyderabad",
        8,
        "2026-11-25",
        "Architect and maintain mission-critical cloud infrastructure, automate deployment pipelines, and optimize containerized microservices."
    ),
    (
        "OPN-ZOHO-04",
        "Zoho Corporation",
        "Full Stack Web Developer",
        json.dumps(["React", "TypeScript", "Node.js", "FastAPI", "PostgreSQL", "REST APIs", "CSS"]),
        json.dumps(["Docker", "Tailwind CSS", "Redis", "Python"]),
        7.0,
        70.0,
        json.dumps(["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science", "Electronics & Communication Engineering"]),
        "10 LPA",
        "Chennai / Tenkasi",
        15,
        "2026-11-30",
        "Develop scalable enterprise SaaS applications, engineer reactive user interfaces, and build high-performance backend APIs."
    ),
    (
        "OPN-BOSCH-05",
        "Bosch Global Software",
        "Embedded Systems & IoT Firmware Engineer",
        json.dumps(["Embedded C", "C++", "Microcontrollers", "RTOS", "IoT Protocols", "CAN Bus", "Circuit Design"]),
        json.dumps(["ARM Cortex-M", "Verilog", "KiCAD", "MQTT"]),
        7.5,
        75.0,
        json.dumps(["Electronics & Communication Engineering", "Mechanical Engineering"]),
        "12 LPA",
        "Coimbatore / Bangalore",
        10,
        "2026-12-05",
        "Develop real-time automotive firmware, telemetry systems, sensor interfaces, and IoT connected device architectures."
    ),
    (
        "OPN-LT-06",
        "Larsen & Toubro (L&T)",
        "Robotics & Industrial Automation Engineer",
        json.dumps(["Robotics", "CAD/CAM", "PLC Programming", "Industrial Automation", "MATLAB", "SolidWorks"]),
        json.dumps(["AutoCAD", "Finite Element Analysis", "Python"]),
        7.0,
        75.0,
        json.dumps(["Mechanical Engineering"]),
        "9.5 LPA",
        "Chennai / Mumbai",
        8,
        "2026-12-10",
        "Program industrial robotic cells, design automated manufacturing machinery, and deploy PLC-driven industrial automation setups."
    ),
    (
        "OPN-TCS-07",
        "TCS Digital",
        "Cybersecurity Analyst & Systems Engineer",
        json.dumps(["Java", "Python", "Cybersecurity", "Network Protocols", "SQL", "Cryptography"]),
        json.dumps(["Spring Boot", "Linux", "Penetration Testing Basics"]),
        7.0,
        70.0,
        json.dumps(["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science", "Electronics & Communication Engineering"]),
        "7.5 LPA",
        "Chennai / Pan India",
        25,
        "2026-12-15",
        "Monitor enterprise security posture, implement cryptographic algorithms, audit networks, and engineer reliable enterprise software."
    ),
    (
        "OPN-RAZOR-08",
        "Razorpay",
        "Frontend Platform Engineer",
        json.dumps(["JavaScript", "TypeScript", "React", "Next.js", "Web Performance", "Tailwind CSS"]),
        json.dumps(["GraphQL", "Node.js", "WebSockets", "CSS"]),
        7.5,
        75.0,
        json.dumps(["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science"]),
        "15 LPA",
        "Bangalore",
        6,
        "2026-11-28",
        "Craft world-class checkout and payment dashboard experiences with sub-second page loads and seamless UX interactivity."
    ),
]
c.executemany("INSERT INTO company_openings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", sample_openings)

# ------------------------------------------------------------------------------
# Student Skills & Placement Profile Table
# ------------------------------------------------------------------------------
c.execute("DROP TABLE IF EXISTS student_skills")
c.execute("""
CREATE TABLE student_skills (
    student_id TEXT PRIMARY KEY,
    primary_skills TEXT NOT NULL,
    secondary_skills TEXT NOT NULL,
    certifications TEXT NOT NULL,
    projects TEXT NOT NULL,
    preferred_role TEXT NOT NULL,
    placement_status TEXT NOT NULL
)
""")

skills_data_by_id = {
    "101": {
        "primary": ["Python", "FastAPI", "React", "PostgreSQL", "SQL", "Git"],
        "secondary": ["Docker", "Tailwind CSS", "Redis", "REST APIs"],
        "certs": ["Meta Front-End Developer Specialization", "PostgreSQL Associate"],
        "projects": ["Campus Placement & ERP Portal", "High-Throughput Redis Cache Proxy"],
        "role": "Full Stack Web Developer",
        "status": "Active Seeking",
    },
    "102": {
        "primary": ["Java", "Python", "HTML", "CSS", "MySQL"],
        "secondary": ["JavaScript", "Git", "Spring Basics"],
        "certs": ["Oracle Certified Associate Java"],
        "projects": ["Student Attendance & Grade Tracker Web App"],
        "role": "Associate Software Engineer",
        "status": "Needs Attendance Condonation",
    },
    "103": {
        "primary": ["C++", "Python", "Go", "Distributed Systems", "Data Structures & Algorithms", "System Design", "SQL"],
        "secondary": ["gRPC", "Docker", "Kubernetes", "Linux Kernel"],
        "certs": ["Google Cloud Professional Cloud Architect", "Certified Kubernetes Administrator (CKA)"],
        "projects": ["Raft Consensus Distributed Key-Value Store", "Multi-Threaded HTTP/2 Proxy in C++"],
        "role": "Backend Software Engineer (SDE-1)",
        "status": "Top Tier Candidate / Seeking",
    },
    "104": {
        "primary": ["Embedded C", "Microcontrollers", "RTOS", "IoT Protocols", "Circuit Design", "MATLAB"],
        "secondary": ["C++", "Python", "KiCAD", "MQTT", "ESP32"],
        "certs": ["ARM Accredited Engineer", "Texas Instruments IoT Specialist"],
        "projects": ["Smart Agriculture IoT Mesh Sensor Gateway", "Quadcopter Flight Controller with STM32"],
        "role": "Embedded Systems & IoT Firmware Engineer",
        "status": "Active Seeking",
    },
    "105": {
        "primary": ["CAD/CAM", "Robotics", "PLC Programming", "Industrial Automation", "SolidWorks", "MATLAB"],
        "secondary": ["AutoCAD", "Python for Engineering", "Additive Manufacturing"],
        "certs": ["Certified SolidWorks Associate (CSWA)", "Siemens PLC Certified"],
        "projects": ["6-DOF Robotic Arm with Computer Vision", "Autonomous AGV Chassis Design"],
        "role": "Robotics & Industrial Automation Engineer",
        "status": "Active Seeking",
    },
    "106": {
        "primary": ["TypeScript", "React", "Next.js", "Node.js", "PostgreSQL", "Tailwind CSS", "JavaScript"],
        "secondary": ["GraphQL", "Prisma", "Docker", "WebSockets"],
        "certs": ["AWS Certified Developer Associate", "Frontend Masters Certified Web Architect"],
        "projects": ["Real-time Collaborative Code Editor", "Microservices E-Commerce Platform"],
        "role": "Frontend Platform Engineer",
        "status": "Pre-Final Year Top Talent",
    },
    "107": {
        "primary": ["Python", "Machine Learning", "Scikit-Learn", "SQL", "Pandas", "Data Analysis"],
        "secondary": ["PyTorch", "Tableau", "FastAPI", "Statistics"],
        "certs": ["TensorFlow Developer Certificate"],
        "projects": ["Customer Churn Prediction Engine", "Financial Time-Series Forecasting Pipeline"],
        "role": "Data Analyst / Junior ML Engineer",
        "status": "Active Seeking",
    },
    "108": {
        "primary": ["AWS", "Docker", "Kubernetes", "Linux", "Python", "CI/CD", "Terraform", "Networking"],
        "secondary": ["Ansible", "Prometheus", "Grafana", "Go", "Bash Scripting"],
        "certs": ["AWS Certified Solutions Architect Associate", "HashiCorp Certified Terraform Associate"],
        "projects": ["Multi-Region Kubernetes Infrastructure with GitOps", "Zero-Downtime Blue-Green Deployment Engine"],
        "role": "Cloud Solutions Architect / DevOps Engineer",
        "status": "Final Year Ready for Placement",
    },
    "109": {
        "primary": ["Embedded C", "C++", "Verilog", "VLSI Architectures", "CAN Bus", "RTOS", "Microcontrollers"],
        "secondary": ["ARM Cortex-M", "FPGA Programming", "Circuit Design", "Signal Processing"],
        "certs": ["Cadence VLSI Design Specialist", "ARM Embedded Systems Expert"],
        "projects": ["FPGA-Accelerated Edge Inference Engine", "Automotive CAN-Bus Telemetry Controller"],
        "role": "Embedded Systems & IoT Firmware Engineer",
        "status": "Gold Medalist / High Priority Candidate",
    },
    "110": {
        "primary": ["Finite Element Analysis", "ANSYS", "CAD/CAM", "Thermal Simulation", "SolidWorks"],
        "secondary": ["Automotive Dynamics", "CNC Programming", "DFM"],
        "certs": ["ANSYS FEA Certified"],
        "projects": ["Formula Student Racecar Aerodynamic Undertray & Spaceframe Optimization"],
        "role": "Core Mechanical Design Engineer",
        "status": "Final Year Seeking",
    },
    "111": {
        "primary": ["Java", "Spring Boot", "Cybersecurity", "Network Protocols", "SQL", "Cryptography"],
        "secondary": ["Python", "Penetration Testing Basics", "Linux", "Docker"],
        "certs": ["CompTIA Security+", "Certified Ethical Hacker (CEH) Practical"],
        "projects": ["Enterprise OAuth2 Microservice Identity Provider", "Network Traffic Anomaly & Intrusion Detection System"],
        "role": "Cybersecurity Analyst & Systems Engineer",
        "status": "Active Seeking",
    },
    "112": {
        "primary": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "Transformers", "SQL", "Statistics"],
        "secondary": ["Hugging Face", "LangChain", "FastAPI", "Vector Databases", "Computer Vision"],
        "certs": ["DeepLearning.AI Deep Learning Specialization", "AWS Certified Machine Learning Specialty"],
        "projects": ["End-to-End Enterprise Neuro-Symbolic RAG QA System", "Multimodal Medical Chest X-Ray Diagnostics Classifier"],
        "role": "Data Scientist / Applied AI Engineer",
        "status": "Active Seeking",
    },
}

sample_student_skills = []
for id_num, data in skills_data_by_id.items():
    for prefix in ["U", "S"]:
        sample_student_skills.append((
            f"{prefix}{id_num}",
            json.dumps(data["primary"]),
            json.dumps(data["secondary"]),
            json.dumps(data["certs"]),
            json.dumps(data["projects"]),
            data["role"],
            data["status"],
        ))

c.executemany("INSERT INTO student_skills VALUES (?,?,?,?,?,?,?)", sample_student_skills)

conn.commit()
conn.close()
print(f"[OK] Created data/students.db with {len(student_rows)} students, {len(sample_staff)} staff, {len(sample_courses)} courses, {len(sample_attendance)} attendance records, {len(sample_exams)} exams, {len(sample_openings)} company openings, and {len(sample_student_skills)} student skill profiles.")

# ══════════════════════════════════════════════════════════════════════════════
# 2. Unstructured College Knowledge (Documents JSON)
# ══════════════════════════════════════════════════════════════════════════════
documents = [
    # Academics & Examination
    {
        "id": "policy_attendance_01",
        "source": "Attendance Policy",
        "text": "AMYPO requires students to maintain a minimum of 75% attendance in each registered theory and laboratory course to be eligible to appear for the semester end examinations. Students falling below 75% will be debarred from writing exams unless an approved medical condonation certificate is submitted within 7 days."
    },
    {
        "id": "policy_attendance_condonation_02",
        "source": "Attendance Condonation Policy",
        "text": "Attendance condonation is permissible for students possessing attendance between 65% and 74.9% on valid medical grounds, official participation in sports, or representing the college in state/national events. Applications must be countersigned by the Head of Department and approved by the Dean of Academics with the prescribed condonation fee."
    },
    {
        "id": "policy_grading_system_01",
        "source": "Academic Grading & CGPA Policy",
        "text": "Academic evaluation follows a 10-point Letter Grade scale: O (Outstanding, 90-100 marks, Grade Point 10.0), A+ (Excellent, 80-89 marks, Grade Point 9.0), A (Very Good, 70-79 marks, Grade Point 8.0), B+ (Good, 60-69 marks, Grade Point 7.0), B (Above Average, 55-59 marks, Grade Point 6.0), C (Pass, 50-54 marks, Grade Point 5.0), and F (Fail/Arrear, below 50 marks, Grade Point 0.0). Continuous Internal Assessment contributes 40% and End Semester Exam contributes 60%."
    },
    {
        "id": "policy_exam_retake_01",
        "source": "Exam Retake & Arrear Policy",
        "text": "Students who secure an 'F' grade or are absent for an end-semester exam may clear the subject in subsequent supplementary or regular semester exam cycles. The arrear examination fee is Rs. 500 per theory subject and Rs. 750 per laboratory subject. Revaluation can be requested within 10 days of results declaration for a fee of Rs. 600 per paper."
    },
    {
        "id": "policy_academic_calendar_01",
        "source": "Academic Calendar & Working Hours",
        "text": "AMYPO operates on a semester schedule: Odd semesters run from July to November, and Even semesters run from January to May. Regular class hours are Monday to Friday, from 8:45 AM to 4:30 PM. Each semester includes two internal continuous assessment tests (CAT-1 and CAT-2) followed by model practical examinations."
    },

    # Fees & Scholarships
    {
        "id": "faq_fee_structure_01",
        "source": "Fee Policy & Payment Details",
        "text": "Semester tuition fees and examination fees must be remitted prior to the start of each semester. A grace period is available until the 10th day of the term. Payments can be made online through the AMYPO Student Portal payment gateway (Net Banking, UPI, Cards) or physically at the Accounts Counter in the Administration Block (open 9:30 AM to 4:00 PM). Late payments incur a fine of Rs. 100 per day."
    },
    {
        "id": "faq_scholarship_01",
        "source": "Scholarships & Financial Assistance",
        "text": "AMYPO offers Merit Scholarships offering a 50% tuition fee waiver to undergraduate students who achieve a CGPA of 9.0 and above with no arrears. Sports Scholarships ranging from 25% to 75% fee waivers are awarded to athletes representing the college at university, state, or national levels. Economically backward students can apply for Dean's Financial Aid through the Student Welfare Office."
    },

    # Facilities & Hours
    {
        "id": "faq_library_01",
        "source": "Central Library Hours & Borrowing Rules",
        "text": "The AMYPO Central Library is open Monday through Friday from 8:30 AM to 7:00 PM, and on Saturdays from 9:00 AM to 1:00 PM. During semester examinations, the library provides extended study hours until 10:00 PM. Undergraduate students can borrow up to 3 books for a duration of 14 days, with one renewal permitted. Overdue books incur a late fine of Rs. 5 per day."
    },
    {
        "id": "faq_digital_library_02",
        "source": "Digital Library & Research Resources",
        "text": "The Digital Library section is situated on the 2nd floor of the Central Library, offering 60 high-speed computer terminals. Students have free on-campus access to IEEE Xplore, ScienceDirect, Springer, DELNET, and NPTEL local video servers. Remote login credentials are provided to all students during orientation."
    },
    {
        "id": "faq_hostel_accommodation_01",
        "source": "Hostel Facilities & Curfew Rules",
        "text": "AMYPO provides secure on-campus residential hostels: Cauvery Block and Krishna Block for boys, and Ganga Block and Yamuna Block for girls. Hostels are equipped with Wi-Fi, study halls, solar hot water, laundry rooms, and dining halls. Curfew (in-time) is strictly 8:30 PM on weekdays and 9:00 PM on weekends with biometric check-in. The hostel fee is Rs. 45,000 per semester inclusive of mess charges."
    },
    {
        "id": "faq_canteen_dining_01",
        "source": "Canteen & Dining Facilities",
        "text": "The central college cafeteria operates daily from 7:30 AM to 8:30 PM serving breakfast, lunch, snacks, and dinner. It features separate vegetarian and multi-cuisine counters offering hygienic, subsidized meals. Additionally, an on-campus Nescafe kiosk near Tech Block-1 provides beverages and quick bites from 8:00 AM to 6:00 PM."
    },
    {
        "id": "faq_sports_gym_01",
        "source": "Sports Complex & Gym Timings",
        "text": "The AMYPO Sports Complex includes a modern gymnasium open in two sessions: Morning from 6:00 AM to 8:30 AM, and Evening from 4:30 PM to 7:30 PM, supervised by certified physical directors. Outdoor facilities feature a 400m synthetic athletic track, football ground, cricket nets, volleyball courts, and two floodlit outdoor basketball courts. Indoor facilities include 4 wooden badminton courts and table tennis."
    },
    {
        "id": "faq_health_center_01",
        "source": "Campus Health Center & Medical Clinic",
        "text": "The Campus Health Center is located on the ground floor of the Student Amenities Block (Room G-04). A full-time registered nurse is stationed 24/7, and a visiting physician is available Monday through Saturday from 9:00 AM to 5:00 PM. Consultation and basic first-aid medicines are free for students. In medical emergencies, the college ambulance can be summoned via internal telephone extension 1100."
    },
    {
        "id": "faq_transport_bus_01",
        "source": "Campus Bus Transportation",
        "text": "AMYPO runs a dedicated fleet of 18 GPS-enabled college buses servicing major transit hubs and neighborhoods across the metropolitan area. Buses arrive at the campus by 8:15 AM and depart at 4:45 PM. A late evening bus departs at 6:00 PM for students using lab and library facilities. Annual bus passes are issued by the Transport Desk located near Security Gate 1."
    },

    # Placements & Career
    {
        "id": "faq_placement_01",
        "source": "Training & Placement Cell Policy",
        "text": "The AMYPO Training and Placement Cell coordinates campus recruitments beginning in the 6th semester. To be eligible for campus drives, students must maintain a minimum CGPA of 6.5 with zero active standing arrears. Comprehensive placement training covers Data Structures, System Design, Quantitative Aptitude, Communication Skills, and Mock Technical Interviews."
    },
    {
        "id": "faq_placement_recruiters_02",
        "source": "Placement Statistics & Top Recruiters",
        "text": "Over 150 leading technology and core engineering enterprises recruit from AMYPO annually, including Amazon, Microsoft, Infosys, TCS, Wipro, Zoho, Cognizant, L&T, and Bosch. The highest domestic salary package achieved was 24 LPA, with an overall campus average package of 6.8 LPA. Over 92% of eligible candidates received placement offers in the previous academic year."
    },
    {
        "id": "faq_internship_policy_01",
        "source": "Internship & Capstone Project Guidelines",
        "text": "Undergraduate engineering students must complete a mandatory 6 to 8 week industrial internship during summer vacation following the 6th semester. The final year Capstone Project is executed in two stages: Project Phase-1 in the 7th semester (literature review and prototype design) and Project Phase-2 in the 8th semester (implementation, testing, and conference publication)."
    },

    # Departments & Administration
    {
        "id": "staff_cse_department_01",
        "source": "Computer Science & Engineering (CSE) Department",
        "text": "The Head of Department (HoD) of Computer Science and Engineering is Dr. Rajesh Kumar, Professor specializing in Distributed Systems and Cloud Computing (Office: Tech Block-1, Room 301). The department houses modern laboratories including the High-Performance AI Lab, Database Systems Lab, and Cloud Infrastructure Center. Year Coordinator is Prof. Anitha Raman (Tech Block-1, Room 305)."
    },
    {
        "id": "staff_ece_department_01",
        "source": "Electronics & Communication Engineering (ECE) Department",
        "text": "The Head of Department (HoD) of Electronics and Communication Engineering is Dr. Meenakshi Sundaram, Professor specializing in VLSI Architectures and Embedded Systems (Office: VLSI Block, Room 201). The department features state-of-the-art IoT Innovation Labs, Microwave Antenna Testing Chambers, and Digital Signal Processing centers."
    },
    {
        "id": "staff_mech_department_01",
        "source": "Mechanical Engineering Department",
        "text": "The Head of Department (HoD) of Mechanical Engineering is Prof. Suresh Babu, Associate Professor specializing in Robotics, CAD/CAM, and Industrial Automation (Office: Workshop Block, Room 101). Facilities include CNC Machining Centers, 3D Printing Prototyping Labs, and Fluid Mechanics & Thermal research test rigs."
    },
    {
        "id": "staff_it_aids_department_01",
        "source": "IT and AI & Data Science Departments",
        "text": "The Information Technology department is headed by Dr. Harish Natarajan (Associate Professor & HoD IT, Tech Block-2, Room 204). The Artificial Intelligence & Data Science department faculty coordinator is Prof. Pooja Nair (Tech Block-2, Room 310), leading research in Deep Learning, Computer Vision, and Natural Language Processing."
    },
    {
        "id": "admin_leadership_01",
        "source": "College Administration & Leadership",
        "text": "The Principal of the college is Dr. K. Radhakrishnan, who serves as the Principal and Director of AMYPO College (Office: Administration Block, Room 101). The Dean of Academics is Dr. Vandana Hegde (Admin Block, Room 102), who oversees curriculum, student affairs, academic policies, and university accreditation. The Controller of Examinations (CoE) is Dr. S. Swaminathan (Examination Cell, Admin Block, Room 204). College administrative and dean offices operate Monday to Friday from 9:00 AM to 5:00 PM."
    },
    {
        "id": "policy_antiragging_01",
        "source": "Anti-Ragging & Student Safety Policy",
        "text": "AMYPO maintains a zero-tolerance policy against ragging, harassment, and discrimination in strict accordance with Supreme Court and UGC directives. The 24/7 Anti-Ragging Toll-Free Helpline is 1800-180-5522. The Campus Flying Squad can be reached at 98765-43210. The Women's Internal Complaints Committee (ICC) is chaired by Dr. Vandana Hegde."
    },
    {
        "id": "faq_student_clubs_01",
        "source": "Student Clubs & Campus Fests",
        "text": "AMYPO features active student clubs: BitByBit (Coding & Hackathons), GDSC AMYPO (Google Developer Student Club), MechaBots (Robotics), Symphony (Music), Mudras (Dance), and Aperture (Photography). The college hosts two premier annual events: 'TechNova', the national-level inter-collegiate technical symposium in March, and 'Aura', the 3-day annual cultural fest in October."
    },

    # Course Content
    {
        "id": "course_dbms_01",
        "source": "DBMS Course Content - Module 3",
        "text": "Module 3 of the Database Management Systems course (CS501) covers Relational Database Design and Normalization, including First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), and Boyce-Codd Normal Form (BCNF), along with functional dependencies and multi-valued dependencies to eliminate data redundancy and insertion/deletion anomalies."
    },
    {
        "id": "course_dbms_02",
        "source": "DBMS Course Content - Module 4 & 5",
        "text": "Module 4 of Database Management Systems covers Transaction Processing and Concurrency Control, emphasizing ACID properties (Atomicity, Consistency, Isolation, Durability), Serializability, Two-Phase Locking (2PL), and Deadlock handling. Module 5 introduces Storage structures, B+ Tree indexing, Query Execution Plans, and NoSQL document stores."
    },
    {
        "id": "faq_college_overview_01",
        "source": "About AMYPO Institute of Technology & Science",
        "text": "AMYPO Institute of Technology & Science is an autonomous, premier engineering college affiliated with the State Technological University and accredited with NAAC 'A++' Grade. AMYPO offers B.Tech and M.Tech degrees in Computer Science, AI & Data Science, Information Technology, Electronics & Communication, and Mechanical Engineering across a lush 60-acre Wi-Fi enabled campus."
    },
    # ── Official Examination Schedules & Timetables ──────────────────────────
    {
        "id": "exam_schedule_semester_end_nov2026",
        "source": "End-Semester Examination Timetable (Nov/Dec 2026)",
        "text": "The Office of the Controller of Examinations has published the official Odd Semester End Examination Timetable (November/December 2026). Key examination dates: The mandatory language paper HS101 Tamil Heritage & Scientific Tamil (Heritage of Tamils / Tamils and Technology) is scheduled on November 24, 2026 (Tuesday) in the forenoon session from 9:30 AM to 12:30 PM in Main Examination Block Rooms A-201 through A-208. CS501 Database Management Systems is on November 27, 2026 (9:30 AM - 12:30 PM). CS502 Operating Systems is on November 30, 2026 (9:30 AM - 12:30 PM). CS503 Theory of Computation / Algorithms is on December 3, 2026 (9:30 AM - 12:30 PM). CS504 Computer Networks is on December 7, 2026 (9:30 AM - 12:30 PM). Practical semester exams take place from November 10 to November 18, 2026. Hall tickets will be issued via the portal from November 15, 2026."
    },
    {
        "id": "exam_tamil_course_schedule_01",
        "source": "Tamil Language Course (HS101) & Exam Schedule",
        "text": "HS101 Tamil Heritage and Scientific Tamil (Heritage of Tamils / Tamils and Technology) is a compulsory curriculum course for undergraduate engineering students. The end-semester written examination date is Tuesday, November 24, 2026, conducted from 9:30 AM to 12:30 PM. The examination syllabus encompasses Sangam classical literature, Tamil rock architecture, historical metallurgy, irrigation engineering, and contemporary technical vocabulary in scientific Tamil. The course coordinator and Controller of Examinations is Dr. S. Swaminathan (Admin Block, Room 204)."
    },
    {
        "id": "exam_cat_internal_schedule_01",
        "source": "Continuous Assessment Tests (CAT-1 & CAT-2) Schedule",
        "text": "Continuous Assessment Tests (CAT) for the current academic session are organized by the Dean of Academics: CAT-1 internal exams are conducted from September 15 to September 20, 2026. CAT-2 internal exams are conducted from October 20 to October 25, 2026. Model practical laboratory exams are scheduled from November 3 to November 8, 2026. Internal assessment marks contribute 40% toward final subject grading."
    },
    {
        "id": "exam_hall_ticket_admit_card_01",
        "source": "Exam Hall Ticket & Rules of Conduct",
        "text": "Hall tickets (Admit Cards) for semester examinations are downloadable through the AMYPO Student Portal 10 days before the exam session (beginning November 15, 2026). Students must possess a minimum of 75% attendance in theory and lab courses to be granted exam eligibility and download hall tickets. Students must report to their assigned exam hall by 9:00 AM with their physical College ID card and signed Hall Ticket. Electronic gadgets, smart watches, and programmable calculators are strictly prohibited."
    },
    # ── Placement & Skill-to-Role Matching System ────────────────────────────
    {
        "id": "policy_placement_role_matching_01",
        "source": "Skill-to-Role Matching & Anti-Random Selection Policy",
        "text": "To prevent random selection and eliminate wasted recruitment chances, AMYPO Training & Placement Cell implements an automated Skill-to-Role Matching Engine. Instead of random batch allocations, candidates are mapped against company opening requirements based on primary skills, secondary skills, verified projects, and academic eligibility (minimum CGPA and 75% attendance). This ensures high selection probability and targeted interview shortlists for corporate recruitment drives."
    },
    {
        "id": "policy_placement_company_openings_02",
        "source": "Campus Placement Corporate Openings & Requirements",
        "text": "AMYPO hosts campus recruitment drives from top companies including Google (SDE Backend - Distributed Systems, Go, Python, Algorithms, 24 LPA), Microsoft (Data Scientist / Applied AI - PyTorch, ML, NLP, 21 LPA), Amazon (Cloud Solutions Architect - AWS, Docker, Kubernetes, CI/CD, 18 LPA), Zoho Corporation (Full Stack Web Developer - React, TypeScript, FastAPI, PostgreSQL, 10 LPA), Bosch Global Software (Embedded Systems & IoT Firmware - Embedded C, RTOS, CAN Bus, 12 LPA), Larsen & Toubro (Robotics & Automation - PLC, CAD/CAM, MATLAB, 9.5 LPA), TCS Digital (Cybersecurity & Systems - Java, Python, Cryptography, 7.5 LPA), and Razorpay (Frontend Platform - React, TypeScript, Next.js, 15 LPA)."
    },
    {
        "id": "policy_placement_student_readiness_03",
        "source": "Student Placement Preparation & Skill Gap Analysis",
        "text": "Students can review their personal skill match percentage and gap analysis for every active company opening on the AMYPO Portal. When a student's skills align closely with a role's required tech stack, their interview clearance rate exceeds 85%. Students are advised to address missing skills identified by the matcher prior to company technical tests to maximize selection odds without burning application limits."
    }
]

with open("data/documents.json", "w") as f:
    json.dump(documents, f, indent=2)

print(f"[OK] Created data/documents.json with {len(documents)} comprehensive college knowledge documents.")
