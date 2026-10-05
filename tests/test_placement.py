import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.placement_engine import (
    calculate_candidate_match,
    get_all_company_openings,
    get_all_students_with_skills,
    get_student_skills_profile,
    suggest_openings_for_student,
    suggest_students_for_opening,
)


class TestPlacementEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_all_company_openings(self):
        openings = get_all_company_openings()
        self.assertGreaterEqual(len(openings), 8)
        companies = [op["company_name"] for op in openings]
        self.assertIn("Google", companies)
        self.assertIn("Microsoft", companies)
        self.assertIn("Amazon", companies)
        self.assertIn("Zoho Corporation", companies)

    def test_get_all_students_with_skills(self):
        students = get_all_students_with_skills()
        self.assertGreaterEqual(len(students), 12)
        s101 = next((s for s in students if s["student_id"] == "U101"), None)
        self.assertIsNotNone(s101)
        self.assertIn("React", s101["primary_skills"])
        self.assertIn("FastAPI", s101["primary_skills"])

    def test_suggest_students_for_google_sde(self):
        result = suggest_students_for_opening("Google", top_n=3)
        self.assertIsNotNone(result.get("opening"))
        self.assertEqual(result["opening"]["company_name"], "Google")
        self.assertGreaterEqual(len(result["matched_students"]), 1)
        # Karthik Raja (U103) has 9.25 CGPA, Go, Distributed Systems, Algorithms -> top match
        top_student = result["matched_students"][0]
        self.assertEqual(top_student["student_id"], "U103")
        self.assertGreaterEqual(top_student["match_percentage"], 85.0)
        self.assertTrue(top_student["is_fully_eligible"])

    def test_suggest_students_for_microsoft_data_scientist(self):
        result = suggest_students_for_opening("Microsoft", top_n=3)
        self.assertIsNotNone(result.get("opening"))
        self.assertEqual(result["opening"]["company_name"], "Microsoft")
        # Aditya Varma (U112) is AI&DS with PyTorch, NLP, Deep Learning, ML
        top_student = result["matched_students"][0]
        self.assertEqual(top_student["student_id"], "U112")
        self.assertGreaterEqual(top_student["match_percentage"], 90.0)

    def test_suggest_students_for_zoho_full_stack(self):
        result = suggest_students_for_opening("Zoho", top_n=3)
        self.assertIsNotNone(result.get("opening"))
        self.assertEqual(result["opening"]["company_name"], "Zoho Corporation")
        student_ids = [s["student_id"] for s in result["matched_students"]]
        # Sneha Patel (U106) and Arun Kumar (U101) should be top candidates
        self.assertTrue("U106" in student_ids or "U101" in student_ids)

    def test_suggest_openings_for_student(self):
        result = suggest_openings_for_student("U101", top_n=3)
        self.assertIsNotNone(result.get("student"))
        self.assertEqual(result["student"]["student_id"], "U101")
        self.assertGreaterEqual(len(result["recommended_openings"]), 1)
        # Arun Kumar has Full Stack (React, FastAPI, PostgreSQL) -> Zoho should be near top
        company_names = [op["company_name"] for op in result["recommended_openings"]]
        self.assertIn("Zoho Corporation", company_names)

    def test_placement_api_endpoints(self):
        # 1. List openings
        res = self.client.get("/api/v1/placement/openings")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("openings", data)
        self.assertGreaterEqual(data["total"], 8)

        # 2. Suggest students for opening
        res = self.client.get("/api/v1/placement/suggest-students?company=Amazon")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["opening"]["company_name"], "Amazon")
        self.assertGreaterEqual(len(data["matched_students"]), 1)

        # 3. Suggest roles for student
        res = self.client.get("/api/v1/placement/suggest-roles?student_id=U103")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["student"]["student_id"], "U103")
        self.assertGreaterEqual(len(data["recommended_openings"]), 1)

        # 4. Student profile
        res = self.client.get("/api/v1/placement/student-profile?student_id=U101")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["student_id"], "U101")
        self.assertIn("primary_skills", data)

    def test_natural_language_placement_query_in_ask_endpoint(self):
        # Inquire about students for Google opening without user_id
        res = self.client.post("/api/v1/ask", json={
            "question": "Suggest students for Google SDE role to avoid random selection",
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["route"], "personal_sql")
        self.assertIn("Google", data["answer"])
        self.assertIn("Karthik Raja", data["answer"])
        self.assertGreaterEqual(data["confidence"], 0.90)

        # Student personalized inquiry with user_id
        res2 = self.client.post("/api/v1/ask", json={
            "question": "Which company roles match my skills best?",
            "user_id": "U101",
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["route"], "personal_sql")
        self.assertIn("Arun Kumar", data2["answer"])
        self.assertIn("Zoho", data2["answer"])


if __name__ == "__main__":
    unittest.main()
