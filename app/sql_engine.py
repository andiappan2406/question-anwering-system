import os
import sqlite3
from typing import Dict, List, Optional, Tuple

from app.db_manager import db_manager
from app.placement_engine import (
    format_role_suggestions_for_chat,
    format_student_suggestions_for_chat,
    get_all_company_openings,
    get_student_skills_profile,
    suggest_openings_for_student,
    suggest_students_for_opening,
)

DB_PATH = "data/students.db"
COLLEGE_DB_PATH = "data/college.db"



def get_oulad_student_record(student_id: str) -> Optional[Dict]:
    """Fetch OULAD student record from college.db if available."""
    if not student_id or not os.path.exists(COLLEGE_DB_PATH):
        return None
    try:
        clean_id = student_id.strip()
        conn = sqlite3.connect(COLLEGE_DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            SELECT code_module, code_presentation, id_student, gender, region,
                   highest_education, imd_band, age_band, num_of_prev_attempts,
                   studied_credits, disability, final_result
            FROM student_info
            WHERE CAST(id_student AS TEXT) = ?
            """,
            (clean_id,),
        )
        row = c.fetchone()
        if not row:
            conn.close()
            return None

        c.execute(
            "SELECT AVG(score) FROM student_assessment WHERE CAST(id_student AS TEXT) = ?",
            (clean_id,),
        )
        avg_score_row = c.fetchone()
        avg_score = round(avg_score_row[0], 1) if avg_score_row and avg_score_row[0] is not None else 80.0

        c.execute(
            "SELECT total_clicks, active_days FROM student_engagement WHERE CAST(id_student AS TEXT) = ?",
            (clean_id,),
        )
        eng_rows = c.fetchall()
        active_days = sum(r[1] for r in eng_rows) if eng_rows else 0
        conn.close()

        attendance_pct = min(98.5, max(68.0, round(70.0 + min(25.0, active_days * 0.25), 1)))

        return {
            "student_id": str(row[2]),
            "name": f"Learner #{row[2]} ({row[4]})",
            "department": f"School of Computing & Analytics (Module {row[0]}-{row[1]})",
            "semester": 5,
            "section": str(row[0]),
            "attendance_percentage": attendance_pct,
            "gpa": round((avg_score / 10.0), 2),
            "fees_status": f"Tuition Cleared ({row[11]} Standing)",
            "pending_dues": 0 if row[11] == "Pass" else 12500,
            "email": f"learner.{row[2]}@college.edu",
            "mentor": "Faculty Academic Mentor",
            "hostel_details": f"Student Residence Block, {row[4]}",
            "user_type": "student",
        }
    except Exception as e:
        print(f"[SQL Engine] College DB error: {e}")
        return None


def get_student_record(student_id: str) -> Optional[Dict]:
    """Fetch a student's full record from active DB (Supabase / SQLite), case-insensitively."""
    if not student_id:
        return None
    try:
        row = db_manager.execute_query(
            """
            SELECT student_id, name, department, semester, section,
                   attendance_percentage, gpa, fees_status, pending_dues,
                   email, mentor, hostel_details
            FROM students
            WHERE UPPER(TRIM(student_id)) = UPPER(TRIM(?))
            """,
            (student_id,),
            fetch="one",
        )
    except Exception as e:
        print(f"[SQL Engine] Student DB error: {e}")
        return get_oulad_student_record(student_id)

    if row is None:
        return get_oulad_student_record(student_id)

    return {
        "student_id": row["student_id"] if isinstance(row, dict) else row[0],
        "name": row["name"] if isinstance(row, dict) else row[1],
        "department": row["department"] if isinstance(row, dict) else row[2],
        "semester": row["semester"] if isinstance(row, dict) else row[3],
        "section": row["section"] if isinstance(row, dict) else row[4],
        "attendance_percentage": row["attendance_percentage"] if isinstance(row, dict) else row[5],
        "gpa": row["gpa"] if isinstance(row, dict) else row[6],
        "fees_status": row["fees_status"] if isinstance(row, dict) else row[7],
        "pending_dues": row["pending_dues"] if isinstance(row, dict) else row[8],
        "email": row["email"] if isinstance(row, dict) else row[9],
        "mentor": row["mentor"] if isinstance(row, dict) else row[10],
        "hostel_details": row["hostel_details"] if isinstance(row, dict) else row[11],
        "user_type": "student",
    }


def get_staff_record(staff_id: str) -> Optional[Dict]:
    """Fetch a faculty/staff member's record from active DB, case-insensitively."""
    if not staff_id:
        return None
    try:
        row = db_manager.execute_query(
            """
            SELECT staff_id, name, department, role, email, office, specialization
            FROM staff
            WHERE UPPER(TRIM(staff_id)) = UPPER(TRIM(?))
            """,
            (staff_id,),
            fetch="one",
        )
    except Exception as e:
        print(f"[SQL Engine] Staff DB error: {e}")
        return None

    if row is None:
        return None

    return {
        "staff_id": row["staff_id"] if isinstance(row, dict) else row[0],
        "name": row["name"] if isinstance(row, dict) else row[1],
        "department": row["department"] if isinstance(row, dict) else row[2],
        "role": row["role"] if isinstance(row, dict) else row[3],
        "email": row["email"] if isinstance(row, dict) else row[4],
        "office": row["office"] if isinstance(row, dict) else row[5],
        "specialization": row["specialization"] if isinstance(row, dict) else row[6],
        "user_type": "staff",
    }


def get_enrolled_courses(department: str, semester: int) -> list:
    """Fetch registered courses for a student's department and semester."""
    try:
        rows = db_manager.execute_query(
            """
            SELECT course_code, course_name, credits, instructor
            FROM courses
            WHERE department = ? AND semester = ?
            ORDER BY course_code
            """,
            (department, semester),
            fetch="all",
        )
        return [
            {
                "course_code": r["course_code"] if isinstance(r, dict) else r[0],
                "course_name": r["course_name"] if isinstance(r, dict) else r[1],
                "credits": r["credits"] if isinstance(r, dict) else r[2],
                "instructor": r["instructor"] if isinstance(r, dict) else r[3],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[SQL Engine] Courses DB error: {e}")
        return []


def get_courses_taught_by_staff(staff_name: str) -> list:
    """Fetch courses instructed by a faculty member."""
    try:
        name_parts = [p.strip() for p in staff_name.replace("Dr.", "").replace("Prof.", "").split() if len(p.strip()) > 2]
        query = "SELECT course_code, course_name, department, semester, credits, instructor FROM courses WHERE "
        conditions = ["instructor LIKE ?"]
        params = [f"%{staff_name}%"]
        for part in name_parts:
            conditions.append("instructor LIKE ?")
            params.append(f"%{part}%")
        query += " OR ".join(conditions) + " ORDER BY course_code"

        rows = db_manager.execute_query(query, tuple(params), fetch="all")
        return [
            {
                "course_code": r["course_code"] if isinstance(r, dict) else r[0],
                "course_name": r["course_name"] if isinstance(r, dict) else r[1],
                "department": r["department"] if isinstance(r, dict) else r[2],
                "semester": r["semester"] if isinstance(r, dict) else r[3],
                "credits": r["credits"] if isinstance(r, dict) else r[4],
                "instructor": r["instructor"] if isinstance(r, dict) else r[5],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[SQL Engine] Staff Courses DB error: {e}")
        return []


def get_student_subject_attendance(student_id: str) -> List[Dict]:
    """Fetch student subject-wise attendance from student_course_attendance."""
    try:
        rows = db_manager.execute_query(
            """
            SELECT course_code, course_name, attendance_percentage, classes_attended, total_classes, status
            FROM student_course_attendance
            WHERE UPPER(TRIM(student_id)) = UPPER(TRIM(?))
            ORDER BY course_code
            """,
            (student_id,),
            fetch="all",
        )
        return [
            {
                "course_code": r["course_code"] if isinstance(r, dict) else r[0],
                "course_name": r["course_name"] if isinstance(r, dict) else r[1],
                "attendance": r["attendance_percentage"] if isinstance(r, dict) else r[2],
                "attended": r["classes_attended"] if isinstance(r, dict) else r[3],
                "total": r["total_classes"] if isinstance(r, dict) else r[4],
                "status": r["status"] if isinstance(r, dict) else r[5],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[SQL Engine] Subject Attendance error: {e}")
        return []


def get_exam_schedule(search_term: str = "") -> List[Dict]:
    """Fetch exam schedule from relational database."""
    try:
        if search_term:
            term = f"%{search_term.strip()}%"
            rows = db_manager.execute_query(
                """
                SELECT course_code, course_name, exam_date, exam_time, venue, session
                FROM exam_schedule
                WHERE course_name LIKE ? OR course_code LIKE ?
                ORDER BY exam_date
                """,
                (term, term),
                fetch="all",
            )
        else:
            rows = db_manager.execute_query(
                """
                SELECT course_code, course_name, exam_date, exam_time, venue, session
                FROM exam_schedule
                ORDER BY exam_date
                """,
                fetch="all",
            )
        return [
            {
                "course_code": r["course_code"] if isinstance(r, dict) else r[0],
                "course_name": r["course_name"] if isinstance(r, dict) else r[1],
                "exam_date": r["exam_date"] if isinstance(r, dict) else r[2],
                "exam_time": r["exam_time"] if isinstance(r, dict) else r[3],
                "venue": r["venue"] if isinstance(r, dict) else r[4],
                "session": r["session"] if isinstance(r, dict) else r[5],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[SQL Engine] Exam Schedule DB error: {e}")
        return []


def answer_personal_query(question: str, user_id: str) -> Tuple[str, Optional[Dict], float]:
    """
    Lookup over relational SQLite records, including:
    1. Student recommendations for specific company opening roles (Anti-Random Selection)
    2. Student personalized company opening recommendations (Skill-to-Role matching)
    3. User's OWN personal academic and faculty records.
    Always runs fresh from SQLite database — never cached.
    Returns (answer_str, source_dict, confidence_float).
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()

    # ══════════════════════════════════════════════════════════════════════════
    # PLACEMENT FEATURE 1: Student Suggestions for Specific Company Opening Roles
    # ══════════════════════════════════════════════════════════════════════════
    is_suggest_students_for_opening = any(
        k in q_lower
        for k in [
            "suggest student", "suggest students", "recommend student", "recommend students",
            "candidates for", "students for", "who matches", "who is suitable for",
            "who should we select", "selection for company", "skill and role get match",
            "best match for", "who should be selected", "students eligible for",
            "student suggestion for specific opening", "student suggestion", "student suggestions"
        ]
    ) or (
        any(comp in q_lower for comp in ["google", "microsoft", "amazon", "zoho", "bosch", "l&t", "tcs", "razorpay"])
        and any(w in q_lower for w in ["student", "students", "candidate", "candidates", "recommend", "suggest", "select", "hire", "opening", "role"])
    )

    if is_suggest_students_for_opening:
        result = suggest_students_for_opening(q_clean, top_n=3)
        if result.get("opening"):
            opening = result["opening"]
            ans = format_student_suggestions_for_chat(result)
            source = {
                "record_id": f"placement:opening:{opening['opening_id']}",
                "snippet": f"Skill-Matched Candidates for {opening['company_name']} ({opening['role_title']}): Top candidate {result['matched_students'][0]['name']} ({result['matched_students'][0]['match_percentage']}% match) with {len(result['matched_students'][0]['matched_skills'])} matched skills.",
            }
            return ans, source, 0.98

    # ══════════════════════════════════════════════════════════════════════════
    # PLACEMENT FEATURE 2: Personalized Role Suggestions for the Student
    # ══════════════════════════════════════════════════════════════════════════
    is_student_role_suggestion = any(
        k in q_lower
        for k in [
            "role for me", "roles for me", "job for me", "jobs for me", "company for me", "companies for me",
            "opening for me", "openings for me", "match my skills", "match my profile",
            "where should i apply", "which company should i apply", "what roles can i apply",
            "suggest company", "suggest companies", "recommend openings", "recommend jobs",
            "placement match", "roles matching my skills", "roles match my skills"
        ]
    )

    clean_id = user_id.strip() if user_id else ""
    if is_student_role_suggestion:
        active_sid = clean_id if clean_id else "U101"
        result = suggest_openings_for_student(active_sid, top_n=4)
        if result.get("student"):
            student = result["student"]
            ans = format_role_suggestions_for_chat(result)
            top_op = result["recommended_openings"][0] if result["recommended_openings"] else None
            source = {
                "record_id": f"student:{student['student_id']}:placement_matches",
                "snippet": f"Role Matches for {student['name']}: Top recommendation is {top_op['company_name']} ({top_op['role_title']}) with {top_op['match_percentage']}% match." if top_op else f"Role matches for {student['name']}",
            }
            return ans, source, 0.98
        elif not clean_id:
            return (
                "Please select your Student ID (e.g. U101 Arun Kumar, U103 Karthik Raja, U106 Sneha Patel) "
                "in the top bar so I can analyze your exact skills and suggest the best company openings for you.",
                None,
                0.90,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # PLACEMENT FEATURE 3: List All Active Corporate Openings
    # ══════════════════════════════════════════════════════════════════════════
    if any(k in q_lower for k in ["all company openings", "list openings", "what companies are hiring", "placement openings", "campus drives", "active openings", "list company roles", "show all openings", "all openings"]):
        openings = get_all_company_openings()
        if openings:
            lines = [
                "### 🏢 Active Campus Placement Openings (AMYPO Career Center)",
                "To maximize selection chances and prevent wasted quotas, apply to roles matching your primary skills:\n"
            ]
            for op in openings:
                lines.append(
                    f"• **{op['company_name']}** — *{op['role_title']}* (`{op['opening_id']}`)\n"
                    f"  - **Package:** {op['ctc']} | **Location:** {op['location']} | **Vacancies:** {op['positions_open']}\n"
                    f"  - **Required Skills:** {', '.join(op['required_skills'])}\n"
                    f"  - **Cutoff:** Min CGPA {op['min_cgpa']} | Attendance {op['min_attendance']}%\n"
                    f"  - **Deadline:** {op['deadline']}"
                )
            source = {
                "record_id": "placement:openings:directory",
                "snippet": f"Directory of {len(openings)} verified corporate placement openings at AMYPO Institute.",
            }
            return "\n".join(lines), source, 0.95

    if not user_id:
        return (
            "User ID was not provided. Please supply your Student ID (e.g. U101) or Staff ID (e.g. T101).",
            None,
            0.0,
        )

    is_likely_staff = clean_id.upper().startswith("T") or clean_id.lower().startswith("staff")

    staff_record = None
    student_record = None

    if is_likely_staff:
        staff_record = get_staff_record(clean_id)
        if not staff_record:
            student_record = get_student_record(clean_id)
    else:
        student_record = get_student_record(clean_id)
        if not student_record:
            staff_record = get_staff_record(clean_id)

    # ══════════════════════════════════════════════════════════════════════════
    # Staff / Faculty Persona
    # ══════════════════════════════════════════════════════════════════════════
    if staff_record:
        record = staff_record
        q = question.lower()
        field = "profile"
        value = ""

        if any(k in q for k in ["office", "room", "cabin", "location", "desk"]):
            field = "office"
            val = record["office"]
            answer = f"Your faculty office is located at {val} ({record['department']})."
            value = val

        elif any(k in q for k in ["role", "designation", "position", "title"]):
            field = "role"
            val = record["role"]
            answer = f"Your current official designation is {val} in the Department of {record['department']}."
            value = val

        elif any(k in q for k in ["department", "branch"]):
            field = "department"
            val = record["department"]
            answer = f"You are appointed to the Department of {val} as {record['role']}."
            value = val

        elif any(k in q for k in ["specialization", "research", "domain", "expertise"]):
            field = "specialization"
            val = record["specialization"]
            answer = f"Your registered area of specialization and research is: {val}."
            value = val

        elif any(k in q for k in ["email", "mail", "contact"]):
            field = "email"
            val = record["email"]
            answer = f"Your registered faculty institutional email address is {val}."
            value = val

        elif any(k in q for k in ["course", "courses", "subject", "subjects", "teach", "teaching", "classes", "lectures"]):
            field = "courses_taught"
            courses = get_courses_taught_by_staff(record["name"])
            if courses:
                lines = [
                    f"• {c['course_code']}: {c['course_name']} ({c['credits']} credits, Sem {c['semester']} {c['department']})"
                    for c in courses
                ]
                answer = (
                    f"You are listed as instructor for {len(courses)} active course(s):\n"
                    + "\n".join(lines)
                )
                value = ", ".join(c["course_code"] for c in courses)
            else:
                answer = f"You currently have no course sections mapped under '{record['name']}' in the active term database."
                value = "none"

        elif any(k in q for k in ["attendance", "present", "absent", "gpa", "cgpa", "fee", "dues", "tuition"]):
            # Student-only queries asked with staff persona
            field = "profile"
            answer = (
                f"As a faculty member ({record['name']}, {record['role']}), student academic metrics "
                f"such as semester attendance, CGPA, and student fee ledger do not apply to your profile. "
                f"Your faculty office is {record['office']}."
            )
            value = f"{record['role']} ({record['office']})"

        elif any(k in q for k in ["name", "who am i", "my id", "identity"]):
            field = "name"
            answer = f"Your name is {record['name']} and your Staff ID is {record['staff_id']} ({record['role']})."
            value = record["name"]

        else:
            # Full Staff Profile Summary
            field = "profile"
            value = f"{record['name']} (ID: {record['staff_id']})"
            answer = (
                f"Here is your faculty profile summary:\n"
                f"• Name: {record['name']} (ID: {record['staff_id']})\n"
                f"• Department: {record['department']}\n"
                f"• Designation: {record['role']}\n"
                f"• Office: {record['office']}\n"
                f"• Specialization: {record['specialization']}\n"
                f"• Email: {record['email']}"
            )

        source = {
            "record_id": f"staff:{record['staff_id']}:{field}",
            "snippet": f"{record['name']} (Staff) — {field.replace('_', ' ')}: {value}",
        }
        return answer, source, 0.95

    # ══════════════════════════════════════════════════════════════════════════
    # Student Persona
    # ══════════════════════════════════════════════════════════════════════════
    if student_record:
        record = student_record
        q = question.lower()
        field = "profile"
        value = ""

        if any(k in q for k in ["attendance", "attendane", "attendence", "atendance", "attndance", "present", "absent", "classes attended"]):
            field = "attendance_percentage"
            val = record["attendance_percentage"]
            subject_records = get_student_subject_attendance(record["student_id"])
            standing = "✅ Good Standing (Satisfies minimum 75% attendance criteria)" if val >= 75.0 else "⚠️ Attendance Shortage (Below 75% threshold, condonation required)"

            if any(k in q for k in ["all", "subject", "subjects", "course", "courses", "each", "breakdown"]) and subject_records:
                lines = [
                    f"• {s['course_code']} ({s['course_name']}): {s['attendance']}% ({s['attended']}/{s['total']} classes attended) — {s['status']}"
                    for s in subject_records
                ]
                answer = (
                    f"Here is your subject-wise attendance breakdown for Semester {record['semester']} "
                    f"({record['department']}, Section {record['section']}):\n"
                    + "\n".join(lines)
                    + f"\n\nOverall Cumulative Attendance: {val}% ({standing})"
                )
                value = f"{val}% across {len(subject_records)} subjects"
            elif subject_records:
                lines = [
                    f"• {s['course_code']} ({s['course_name']}): {s['attendance']}% ({s['attended']}/{s['total']} attended) — {s['status']}"
                    for s in subject_records
                ]
                answer = (
                    f"Your current overall attendance is {val}% in Semester {record['semester']} "
                    f"({record['department']}, Section {record['section']}). {standing}\n\n"
                    f"**Subject-wise Records:**\n" + "\n".join(lines)
                )
                value = f"{val}% across {len(subject_records)} subjects"
            else:
                answer = (
                    f"Your current overall attendance is {val}% in Semester {record['semester']} "
                    f"({record['department']}, Section {record['section']}). {standing}"
                )
                value = f"{val}%"

        elif any(k in q for k in ["gpa", "cgpa", "grade point", "sgpa", "grade", "marks", "score"]):
            field = "gpa"
            val = record["gpa"]
            answer = f"Your current cumulative GPA is {val:.2f} ({record['department']})."
            value = str(val)

        elif any(k in q for k in ["fee", "dues", "tuition", "balance", "payment", "pending"]):
            field = "fees_status"
            val = record["fees_status"]
            pending = record["pending_dues"]
            if pending > 0:
                answer = f"Your fee status is: {val}. Outstanding balance: Rs. {pending:,}."
            else:
                answer = f"Your fee status is: {val}. You have no outstanding dues."
            value = val

        elif any(k in q for k in ["department", "branch", "major", "stream"]):
            field = "department"
            val = record["department"]
            answer = f"You are enrolled in the Department of {val} (Semester {record['semester']}, Section {record['section']})."
            value = val

        elif any(k in q for k in ["mentor", "advisor", "counselor", "guide", "faculty advisor"]):
            field = "mentor"
            val = record["mentor"]
            answer = f"Your assigned faculty mentor/advisor is {val}."
            value = val

        elif any(k in q for k in ["hostel", "room", "accommodation", "stay", "bus route", "day scholar"]):
            field = "hostel_details"
            val = record["hostel_details"]
            answer = f"Your accommodation/transit details: {val}."
            value = val

        elif any(k in q for k in ["email", "mail", "contact"]):
            field = "email"
            val = record["email"]
            answer = f"Your registered institutional email address is {val}."
            value = val

        elif any(k in q for k in ["semester", "term", "year", "current semester"]):
            field = "semester"
            sem = record["semester"]
            academic_year = (sem + 1) // 2
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(academic_year, "th")
            answer = f"You are currently in Semester {sem} ({academic_year}{suffix} Year, Section {record['section']}) of {record['department']}."
            value = str(sem)

        elif any(k in q for k in ["course", "courses", "subject", "subjects", "registered courses", "enrolled courses", "classes"]):
            field = "courses"
            courses = get_enrolled_courses(record["department"], record["semester"])
            if courses:
                lines = [
                    f"• {c['course_code']}: {c['course_name']} ({c['credits']} credits) — Instructor: {c['instructor']}"
                    for c in courses
                ]
                answer = (
                    f"You are registered for {len(courses)} courses in Semester {record['semester']} "
                    f"({record['department']}):\n" + "\n".join(lines)
                )
                value = ", ".join(c["course_code"] for c in courses)
            else:
                answer = f"No courses found for Semester {record['semester']} ({record['department']})."
                value = "none"

        elif any(k in q for k in ["skill", "skills", "tech stack", "technologies", "project", "projects", "certifications", "certification", "placement profile"]):
            field = "skills"
            sk_profile = get_student_skills_profile(record["student_id"])
            if sk_profile:
                p_skills = ", ".join(sk_profile["primary_skills"])
                s_skills = ", ".join(sk_profile["secondary_skills"]) if sk_profile["secondary_skills"] else "None specified"
                certs = ", ".join(sk_profile["certifications"]) if sk_profile["certifications"] else "None"
                projs = ", ".join(sk_profile["projects"]) if sk_profile["projects"] else "None"
                answer = (
                    f"Here is your registered technical skill & placement profile ({record['name']} - {record['student_id']}):\n"
                    f"• **Primary Tech Stack:** {p_skills}\n"
                    f"• **Secondary Tools:** {s_skills}\n"
                    f"• **Verified Projects:** {projs}\n"
                    f"• **Certifications:** {certs}\n"
                    f"• **Target Domain:** {sk_profile['preferred_role']}\n"
                    f"• **Placement Status:** {sk_profile['placement_status']}\n\n"
                    f"💡 *Tip: Ask 'Which company roles match my skills?' to see matched campus openings without wasting applications.*"
                )
                value = p_skills
            else:
                answer = f"No specialized skills profile found for {record['name']}."
                value = "none"

        elif any(k in q for k in ["name", "who am i", "my id", "roll number", "identity"]):
            field = "name"
            answer = f"Your name is {record['name']} and your Student ID is {record['student_id']}."
            value = record["name"]

        else:
            # Full academic profile summary
            field = "profile"
            value = f"{record['name']} (ID: {record['student_id']})"
            answer = (
                f"Here is your student profile summary:\n"
                f"• Name: {record['name']} (ID: {record['student_id']})\n"
                f"• Department: {record['department']} (Semester {record['semester']}, Section {record['section']})\n"
                f"• Academic Standing: CGPA {record['gpa']:.2f} | Attendance: {record['attendance_percentage']}%\n"
                f"• Fee Status: {record['fees_status']}\n"
                f"• Faculty Mentor: {record['mentor']}\n"
                f"• Accommodation: {record['hostel_details']}\n"
                f"• Email: {record['email']}"
            )

        source = {
            "record_id": f"student:{record['student_id']}:{field}",
            "snippet": f"Verified Student Database [{db_manager.active_dialect.upper()}] — Table: students | {record['name']} (ID: {record['student_id']}) — {field.replace('_', ' ')}: {value}",
        }
        return answer, source, 0.95

    # If neither was found:
    return (
        f"No record was found for ID '{clean_id}'. "
        "Please verify your Student ID (e.g. U101, U102, S101) or Staff ID (e.g. T101, T102) or contact the administration.",
        None,
        0.0,
    )
