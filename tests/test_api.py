import unittest
from fastapi.testclient import TestClient
from app.main import app, cache


class TestFastApiEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        # Clear cache entries before each test to ensure determinism
        cache.entries = []

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["router"], "neuro-symbolic")
        self.assertEqual(data["retriever"], "ready")
        self.assertGreater(data["documents"], 0)

    def test_empty_question_returns_400(self):
        response = self.client.post("/api/v1/ask", json={"question": "   "})
        self.assertEqual(response.status_code, 400)

    def test_chitchat_greeting(self):
        response = self.client.post("/api/v1/ask", json={"question": "Hello there!"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "chitchat")
        self.assertEqual(data["confidence"], 1.0)
        self.assertIn("AMYPO", data["answer"])
        self.assertEqual(len(data["sources"]), 0)

    def test_personal_sql_with_user_id(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What is my current attendance?", "user_id": "U101"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "personal_sql")
        self.assertIn("84.5%", data["answer"])
        self.assertGreaterEqual(data["confidence"], 0.90)
        self.assertGreaterEqual(len(data["sources"]), 1)
        self.assertIn("attendance", data["sources"][0]["record_id"])
        self.assertIsNotNone(data["offload_plan"])
        self.assertGreaterEqual(len(data["offload_plan"]), 1)
        self.assertIsNotNone(data.get("execution_steps"))
        self.assertGreaterEqual(len(data.get("execution_steps", [])), 1)

    def test_personal_sql_without_user_id(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What is my GPA?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "personal_sql")
        self.assertIn("Student ID", data["answer"])
        self.assertIn("personal academic records", data["answer"])
        self.assertEqual(len(data["sources"]), 0)

    def test_personal_registered_courses(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What are my registered courses?", "user_id": "U101"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "personal_sql")
        self.assertIn("Database Management Systems", data["answer"])
        self.assertIn("CS501", data["answer"])

    def test_vector_rag_query(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What are the central library hours?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "vector_rag")
        self.assertGreaterEqual(data["confidence"], 0.40)
        self.assertIn("Library", data["answer"])
        self.assertGreaterEqual(len(data["sources"]), 1)

    def test_semantic_cache_hit_on_repeat_query(self):
        q = "What is the policy for exam attendance?"
        res1 = self.client.post("/api/v1/ask", json={"question": q})
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["route"], "vector_rag")

        # Second identical query must hit semantic cache
        res2 = self.client.post("/api/v1/ask", json={"question": q})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["route"], "cache_hit")
        self.assertEqual(data2["answer"], res1.json()["answer"])

    def test_hybrid_cross_domain_query(self):
        response = self.client.post(
            "/api/v1/ask",
            json={
                "question": "Is my attendance high enough for the semester exams according to college policy?",
                "user_id": "U101",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "hybrid")
        self.assertIn("84.5%", data["answer"])
        self.assertGreaterEqual(len(data["sources"]), 2)
        # Should contain both SQL student source and policy vector source
        record_ids = [s["record_id"] for s in data["sources"]]
        self.assertTrue(any("student:" in r for r in record_ids))
        self.assertTrue(any("policy" in r for r in record_ids))

    def test_ungrounded_query_refusal(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What is the secret recipe of quantum teleportation cookies in 3099?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("don't have enough grounded information", data["answer"])
        self.assertEqual(len(data["sources"]), 0)
        self.assertEqual(data["confidence"], 0.0)

    def test_personal_sql_staff_query(self):
        response = self.client.post(
            "/api/v1/ask",
            json={"question": "What is my office location?", "user_id": "T101"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["route"], "personal_sql")
        self.assertIn("Room 301", data["answer"])
        self.assertTrue(any("staff:T101:office" in s["record_id"] for s in data["sources"]))


if __name__ == "__main__":
    unittest.main()
