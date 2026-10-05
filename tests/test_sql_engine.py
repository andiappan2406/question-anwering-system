import unittest
from app.sql_engine import (
    answer_personal_query,
    get_courses_taught_by_staff,
    get_enrolled_courses,
    get_staff_record,
    get_student_record,
)


class TestSqlEngine(unittest.TestCase):

    # ── Student Record Tests ──────────────────────────────────────────────────

    def test_get_student_record_valid(self):
        record = get_student_record("U101")
        self.assertIsNotNone(record)
        self.assertEqual(record["student_id"], "U101")
        self.assertEqual(record["name"], "Arun Kumar")
        self.assertEqual(record["department"], "Computer Science & Engineering")
        self.assertEqual(record["semester"], 5)
        self.assertGreater(record["attendance_percentage"], 80)
        self.assertGreater(record["gpa"], 8.0)

    def test_get_student_record_case_insensitive(self):
        record = get_student_record("u101")
        self.assertIsNotNone(record)
        self.assertEqual(record["student_id"], "U101")

    def test_get_student_record_nonexistent(self):
        record = get_student_record("UNKNOWN_999")
        self.assertIsNone(record)

    def test_get_student_record_empty(self):
        record = get_student_record("")
        self.assertIsNone(record)

    def test_get_enrolled_courses_valid(self):
        courses = get_enrolled_courses("Computer Science & Engineering", 5)
        self.assertGreater(len(courses), 0)
        codes = [c["course_code"] for c in courses]
        self.assertIn("CS501", codes)
        self.assertIn("CS502", codes)

    def test_get_enrolled_courses_invalid_semester(self):
        courses = get_enrolled_courses("Computer Science & Engineering", 99)
        self.assertEqual(courses, [])

    def test_answer_personal_attendance(self):
        answer, source, conf = answer_personal_query("What is my attendance?", "U101")
        self.assertIn("84.5%", answer)
        self.assertIsNotNone(source)
        self.assertIn("attendance", source["record_id"])
        self.assertGreaterEqual(conf, 0.90)

    def test_answer_personal_gpa(self):
        answer, source, conf = answer_personal_query("What is my GPA?", "U101")
        self.assertIn("8.40", answer)
        self.assertIsNotNone(source)
        self.assertIn("gpa", source["record_id"])
        self.assertGreaterEqual(conf, 0.90)

    def test_answer_personal_fees(self):
        answer, source, conf = answer_personal_query("What is my fee status?", "U101")
        self.assertIn("fee status", answer.lower())
        self.assertIn("No outstanding dues", answer)

    def test_answer_personal_fees_pending(self):
        answer, source, conf = answer_personal_query("Do I have pending fee dues?", "U102")
        self.assertIn("Outstanding balance", answer)

    def test_answer_personal_enrolled_courses(self):
        answer, source, conf = answer_personal_query("What are my registered courses?", "U101")
        self.assertIn("CS501", answer)
        self.assertIn("Database Management Systems", answer)
        self.assertIsNotNone(source)
        self.assertIn("courses", source["record_id"])

    def test_answer_personal_mentor(self):
        answer, source, conf = answer_personal_query("Who is my faculty mentor?", "U101")
        self.assertIn("Dr. Rajesh Kumar", answer)

    def test_answer_personal_hostel(self):
        answer, source, conf = answer_personal_query("What are my hostel details?", "U101")
        self.assertIn("Cauvery", answer)

    def test_answer_personal_semester(self):
        answer, source, conf = answer_personal_query("Which semester am I in?", "U101")
        self.assertIn("Semester 5", answer)

    def test_answer_personal_who_am_i(self):
        answer, source, conf = answer_personal_query("Who am I?", "U101")
        self.assertIn("Arun Kumar", answer)
        self.assertIn("U101", answer)

    def test_answer_personal_full_profile(self):
        answer, source, conf = answer_personal_query("Tell me my details", "U101")
        self.assertIn("student profile summary", answer.lower())
        self.assertIn("Arun Kumar", answer)
        self.assertIn("Cauvery", answer)

    # ── Staff / Faculty Tests ─────────────────────────────────────────────────

    def test_get_staff_record_valid(self):
        record = get_staff_record("T101")
        self.assertIsNotNone(record)
        self.assertEqual(record["staff_id"], "T101")
        self.assertEqual(record["name"], "Dr. Rajesh Kumar")
        self.assertEqual(record["department"], "Computer Science & Engineering")
        self.assertIn("Room 301", record["office"])

    def test_get_staff_record_alias(self):
        record = get_staff_record("staff_fac_4402")
        self.assertIsNotNone(record)
        self.assertEqual(record["name"], "Dr. Rajesh Kumar")

    def test_get_courses_taught_by_staff(self):
        courses = get_courses_taught_by_staff("Dr. Rajesh Kumar")
        self.assertGreater(len(courses), 0)
        codes = [c["course_code"] for c in courses]
        self.assertIn("CS501", codes)

    def test_answer_staff_office(self):
        answer, source, conf = answer_personal_query("What is my office location?", "T101")
        self.assertIn("Room 301", answer)
        self.assertIsNotNone(source)
        self.assertIn("staff:T101:office", source["record_id"])
        self.assertGreaterEqual(conf, 0.90)

    def test_answer_staff_role(self):
        answer, source, conf = answer_personal_query("What is my designation and role?", "T101")
        self.assertIn("Professor & Head of Department", answer)
        self.assertIn("staff:T101:role", source["record_id"])

    def test_answer_staff_department(self):
        answer, source, conf = answer_personal_query("Which department do I belong to?", "T101")
        self.assertIn("Computer Science & Engineering", answer)
        self.assertIn("staff:T101:department", source["record_id"])

    def test_answer_staff_specialization(self):
        answer, source, conf = answer_personal_query("What is my research specialization?", "T101")
        self.assertIn("Distributed Systems", answer)
        self.assertIn("staff:T101:specialization", source["record_id"])

    def test_answer_staff_courses_taught(self):
        answer, source, conf = answer_personal_query("What courses do I teach this semester?", "T101")
        self.assertIn("CS501", answer)
        self.assertIn("staff:T101:courses_taught", source["record_id"])

    def test_answer_staff_attendance_query(self):
        # Academic student query directed at faculty persona
        answer, source, conf = answer_personal_query("What is my attendance percentage?", "T101")
        self.assertIn("faculty member", answer.lower())
        self.assertIn("do not apply", answer.lower())

    def test_answer_staff_who_am_i(self):
        answer, source, conf = answer_personal_query("Who am I?", "T101")
        self.assertIn("Dr. Rajesh Kumar", answer)
        self.assertIn("T101", answer)

    def test_answer_staff_profile(self):
        answer, source, conf = answer_personal_query("Show me my faculty details", "T101")
        self.assertIn("faculty profile summary", answer.lower())
        self.assertIn("Dr. Rajesh Kumar", answer)
        self.assertIn("Tech Block-1", answer)

    def test_answer_personal_nonexistent_id(self):
        answer, source, conf = answer_personal_query("What is my GPA?", "NONEXISTENT_999")
        self.assertIn("No record was found", answer)
        self.assertIsNone(source)
        self.assertEqual(conf, 0.0)

    def test_oulad_student_11391(self):
        record = get_student_record("11391")
        self.assertIsNotNone(record)
        self.assertEqual(record["student_id"], "11391")
        self.assertIn("East Anglian", record["name"])
        self.assertGreater(record["attendance_percentage"], 70)
        self.assertGreater(record["gpa"], 7.0)

    def test_oulad_personal_attendance(self):
        answer, source, conf = answer_personal_query("What is my current attendance?", "11391")
        self.assertIn("attendance is", answer)
        self.assertIsNotNone(source)
        self.assertEqual(source["record_id"], "student:11391:attendance_percentage")

    def test_staff_fac_4402_office(self):
        answer, source, conf = answer_personal_query("What is my office location?", "staff_fac_4402")
        self.assertIn("Tech Block-1", answer)
        self.assertEqual(source["record_id"], "staff:staff_fac_4402:office")


if __name__ == "__main__":
    unittest.main()
