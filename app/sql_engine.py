import sqlite3

DB_PATH = "data/students.db"


def get_student_record(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT student_id, name, attendance_percentage, gpa, semester "
        "FROM students WHERE student_id = ?",
        (student_id,),
    )
    row = c.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "student_id": row[0],
        "name": row[1],
        "attendance_percentage": row[2],
        "gpa": row[3],
        "semester": row[4],
    }


def answer_personal_query(question, student_id):
    """
    Simple keyword-based lookup over the student's OWN record.
    Always runs fresh from the database -- never cached.
    """
    record = get_student_record(student_id)
    if record is None:
        return None, None, 0.0

    q = question.lower()
    if "attendance" in q:
        field = "attendance_percentage"
        answer = f"Your current attendance is {record[field]}%."
    elif "gpa" in q or "cgpa" in q:
        field = "gpa"
        answer = f"Your current GPA is {record[field]}."
    elif "semester" in q:
        field = "semester"
        answer = f"You are currently in semester {record[field]}."
    else:
        return None, None, 0.0

    source = {
        "record_id": f"student:{record['student_id']}:{field}",
        "snippet": f"{record['name']} - {field.replace('_', ' ')}: {record[field]}",
    }
    return answer, source, 0.95
