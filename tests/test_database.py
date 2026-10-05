import unittest
from fastapi.testclient import TestClient

from app.db_manager import db_manager
from app.main import app
from app.router.schemas import DatabaseDialect, DynamicQueryPayload


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_db_manager_connection_and_dialect(self):
        """Verify DB manager initializes with a valid dialect and connection."""
        self.assertIn(db_manager.dialect, [DatabaseDialect.SUPABASE, DatabaseDialect.POSTGRESQL, DatabaseDialect.SQLITE])
        self.assertTrue(db_manager.is_connected)

    def test_db_manager_health_status(self):
        """Verify get_health_status returns structured live metrics."""
        health = db_manager.get_health_status()
        self.assertTrue(health.connected)
        self.assertGreater(health.total_records, 0)
        self.assertIn("students", health.active_tables)
        self.assertIn("company_openings", health.active_tables)
        self.assertIn("student_skills", health.active_tables)

    def test_query_students_table(self):
        """Verify querying students table returns correct format and records."""
        rows = db_manager.execute_query("SELECT student_id, name, department, gpa FROM students ORDER BY student_id ASC LIMIT 5")
        self.assertIsInstance(rows, list)
        self.assertGreaterEqual(len(rows), 1)
        self.assertIn("student_id", rows[0])
        self.assertIn("name", rows[0])
        self.assertIn("gpa", rows[0])

    def test_query_company_openings(self):
        """Verify company openings table can be queried."""
        openings = db_manager.execute_query("SELECT opening_id, company_name, role_title FROM company_openings LIMIT 3")
        self.assertIsInstance(openings, list)
        self.assertGreaterEqual(len(openings), 1)
        self.assertIn("company_name", openings[0])

    def test_dynamic_query_execution(self):
        """Verify dynamic query execution with filters and columns."""
        payload = DynamicQueryPayload(
            table="students",
            columns=["student_id", "name", "department"],
            filters={"student_id": "U101"},
            limit=1,
        )
        res = db_manager.query_dynamic(payload)
        self.assertEqual(res["table"], "students")
        self.assertGreaterEqual(res["count"], 1)
        self.assertEqual(res["rows"][0]["student_id"], "U101")

    def test_api_database_status_endpoint(self):
        """Verify GET /api/v1/database/status returns valid health payload."""
        response = self.client.get("/api/v1/database/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["connected"])
        self.assertIn("engine", data)
        self.assertIn("active_tables", data)
        self.assertGreater(data["total_records"], 0)

    def test_api_database_query_endpoint(self):
        """Verify POST /api/v1/database/query returns filtered rows."""
        payload = {
            "table": "company_openings",
            "columns": ["opening_id", "company_name", "role_title"],
            "filters": {"company_name": "Google"},
            "limit": 5,
        }
        response = self.client.post("/api/v1/database/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["table"], "company_openings")
        self.assertGreaterEqual(data["count"], 1)
        self.assertEqual(data["rows"][0]["company_name"], "Google")


if __name__ == "__main__":
    unittest.main()
