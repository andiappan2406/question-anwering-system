import unittest
from app.router import (
    ContextItem,
    DatabaseRegistry,
    DatabaseTargetType,
    DataPriority,
    NeuroSymbolicRouter,
    RouteType,
    RouterInput,
    StructuredContextSorter,
    classify_intent,
    get_router,
)


class TestNeuroSymbolicRouter(unittest.TestCase):

    def setUp(self):
        self.router = get_router()

    def test_sql_routing_personal_gpa(self):
        input_data = RouterInput(raw_query="What is my current GPA in semester 3?", user_id="STU001")
        decision = self.router.route(input_data)

        self.assertEqual(decision.primary_route, RouteType.SQL)
        self.assertGreaterEqual(decision.confidence, 0.85)
        self.assertGreaterEqual(len(decision.offload_plan), 1)

        sql_target = decision.offload_plan[0]
        self.assertEqual(sql_target.target_id, DatabaseRegistry.TARGET_PERSONAL_SQL)
        self.assertEqual(sql_target.engine_type, DatabaseTargetType.RELATIONAL_SQL)
        self.assertEqual(sql_target.required_parameters.get("user_id"), "STU001")
        self.assertEqual(sql_target.priority, DataPriority.CRITICAL)
        self.assertEqual(sql_target.privacy_level, "confidential")

    def test_sql_routing_attendance(self):
        input_data = "Show me my attendance percentage"
        decision = self.router.route(input_data, user_id="STU102")

        self.assertEqual(decision.primary_route, RouteType.SQL)
        self.assertTrue(any("attendance" in trace for trace in decision.reasoning_trace))
        self.assertGreater(len(decision.execution_steps), 0)

    def test_rag_routing_campus_policy(self):
        input_data = RouterInput(raw_query="What is the refund policy for hostel accommodation fee?")
        decision = self.router.route(input_data)

        self.assertEqual(decision.primary_route, RouteType.RAG)
        self.assertEqual(len(decision.offload_plan), 1)

        rag_target = decision.offload_plan[0]
        self.assertEqual(rag_target.target_id, DatabaseRegistry.TARGET_CAMPUS_VECTOR)
        self.assertEqual(rag_target.engine_type, DatabaseTargetType.VECTOR_STORE)
        self.assertTrue(rag_target.cacheable)
        self.assertEqual(rag_target.privacy_level, "public")

    def test_hybrid_routing_cross_domain(self):
        input_data = RouterInput(
            raw_query="Is my attendance high enough according to the minimum college policy requirement?",
            user_id="STU005",
        )
        decision = self.router.route(input_data)

        self.assertEqual(decision.primary_route, RouteType.HYBRID)
        self.assertEqual(len(decision.offload_plan), 2)

        # Verify both databases are scheduled in sorted priority order
        target_ids = [t.target_id for t in decision.offload_plan]
        self.assertIn(DatabaseRegistry.TARGET_PERSONAL_SQL, target_ids)
        self.assertIn(DatabaseRegistry.TARGET_CAMPUS_VECTOR, target_ids)

        # SQL offload must have higher or equal priority rank (CRITICAL/HIGH <= MEDIUM)
        self.assertLessEqual(decision.offload_plan[0].priority.value, decision.offload_plan[1].priority.value)

    def test_structured_context_sorting(self):
        item1 = ContextItem(
            source_id="faq_001",
            database_target="db_campus_knowledge_vector",
            snippet="Attendance policy doc",
            relevance_score=0.92,
            priority=DataPriority.MEDIUM,
            timestamp=100.0,
        )
        item2 = ContextItem(
            source_id="student:STU001:attendance",
            database_target="db_personal_students_sql",
            snippet="Attendance is 85%",
            relevance_score=0.95,
            priority=DataPriority.CRITICAL,
            timestamp=105.0,
        )
        item3 = ContextItem(
            source_id="faq_002",
            database_target="db_campus_knowledge_vector",
            snippet="Exam rules doc",
            relevance_score=0.98,
            priority=DataPriority.HIGH,
            timestamp=102.0,
        )

        batch = StructuredContextSorter.create_sorted_batch(
            query="Check my attendance against exam rules",
            route=RouteType.HYBRID,
            items=[item1, item2, item3],
        )

        self.assertEqual(batch.total_items, 3)
        # Sorting check: CRITICAL (item2) -> HIGH (item3) -> MEDIUM (item1)
        self.assertEqual(batch.items[0].source_id, "student:STU001:attendance")
        self.assertEqual(batch.items[1].source_id, "faq_002")
        self.assertEqual(batch.items[2].source_id, "faq_001")

    def test_sorting_tie_breaking(self):
        # Two items with same priority, different relevance scores
        item_high_score = ContextItem(
            source_id="faq_a",
            database_target="db_campus_knowledge_vector",
            snippet="Relevant snippet A",
            relevance_score=0.95,
            priority=DataPriority.HIGH,
            timestamp=100.0,
        )
        item_lower_score = ContextItem(
            source_id="faq_b",
            database_target="db_campus_knowledge_vector",
            snippet="Relevant snippet B",
            relevance_score=0.75,
            priority=DataPriority.HIGH,
            timestamp=100.0,
        )

        sorted_items = StructuredContextSorter.sort_context_items([item_lower_score, item_high_score])
        self.assertEqual(sorted_items[0].source_id, "faq_a")
        self.assertEqual(sorted_items[1].source_id, "faq_b")

    def test_query_sanitization(self):
        inp = RouterInput(raw_query="   What   is   my   GPA?   \n\t")
        self.assertEqual(inp.sanitized_query, "What is my GPA?")

    def test_database_registry_profiles(self):
        sql_profile = DatabaseRegistry.get_database_profile(DatabaseRegistry.TARGET_PERSONAL_SQL)
        self.assertEqual(sql_profile["privacy_level"], "confidential")
        self.assertFalse(sql_profile["cacheable"])

        vector_profile = DatabaseRegistry.get_database_profile(DatabaseRegistry.TARGET_CAMPUS_VECTOR)
        self.assertEqual(vector_profile["privacy_level"], "public")
        self.assertTrue(vector_profile["cacheable"])

    def test_legacy_classify_intent_compatibility(self):
        self.assertEqual(classify_intent("What is my attendance?"), "personal")
        self.assertEqual(classify_intent("What is the library timing?"), "common")


if __name__ == "__main__":
    unittest.main()
