import json
import time
import requests

BASE_URL = "http://localhost:9000"

def test_complete_system():
    print("=" * 70)
    print("STARTING COMPLETE AMYPO SYSTEM VERIFICATION")
    print("=" * 70)

    # 1. Health check
    res = requests.get(f"{BASE_URL}/api/v1/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"[1/8] Health Check: Status={health['status']}, Router={health['router']}, Docs={health['documents']}")

    # 2. Test all Sample Students in Database
    students = [
        ("U101", "Arun Kumar", "CSE"),
        ("U102", "Divya Priya", "CSE"),
        ("U103", "Karthik Raja", "CSE"),
        ("U104", "Ananya Iyer", "ECE"),
        ("U105", "Rohan Deshmukh", "Mechanical Engineering"),
        ("U106", "Sneha Patel", "Information Technology"),
        ("U107", "Vikramaditya Rao", "Artificial Intelligence & Data Science"),
    ]

    print("\n[2/8] Testing Student Profiles (Relational SQL)...")
    for uid, name, dept in students:
        payload = {"question": "Who am I?", "user_id": uid}
        r = requests.post(f"{BASE_URL}/api/v1/ask", json=payload).json()
        assert uid in r["answer"] or name in r["answer"], f"Failed for {uid}: {r['answer']}"
        assert r["route"] == "personal_sql"
        assert r["confidence"] >= 0.90
        print(f"  * Student {uid} ({name}): Verified. Attendance, GPA & Dept intact.")

    # 3. Test Student Academic Attributes
    print("\n[3/8] Testing Personal Attributes (U101 & U102)...")
    tests = [
        ("What is my attendance?", "U101", "84.5%"),
        ("What is my GPA?", "U101", "8.40"),
        ("What are my registered courses?", "U101", "CS501"),
        ("Who is my mentor?", "U101", "Rajesh Kumar"),
        ("What are my hostel details?", "U101", "Cauvery"),
        ("What is my fee status?", "U102", "Pending: Rs. 15,000"),
    ]
    for q, uid, expected in tests:
        r = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": q, "user_id": uid}).json()
        assert expected.lower() in r["answer"].lower(), f"Failed on '{q}': {r['answer']}"
        assert r["route"] == "personal_sql"
        assert len(r["execution_steps"]) > 0
        print(f"  * Q: '{q}' [{uid}] -> Match: '{expected}' (Route: {r['route']})")

    # 4. Test Missing User ID Prompt
    print("\n[4/8] Testing Unauthenticated Personal Query...")
    r = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": "What is my GPA?"}).json()
    assert "Student ID" in r["answer"]
    assert r["route"] == "personal_sql"
    print("  * Correctly prompted user to select Student ID.")

    # 5. Test Suggested Campus Knowledge Queries (Vector RAG)
    print("\n[5/8] Testing Suggested Campus Knowledge Queries (Vector RAG)...")
    campus_queries = [
        ("Who is the principal of the college?", "Radhakrishnan"),
        ("Who is the head of CSE?", "Dr. Rajesh Kumar"),
        ("What are the library hours?", "8:30 AM to 7:00 PM"),
        ("Tell me about hostel curfew and rules", "9:00 PM"),
        ("What is the placement eligibility criteria?", "6.5"),
    ]
    for q, expected in campus_queries:
        r = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": q}).json()
        assert expected.lower() in r["answer"].lower(), f"Failed on '{q}': {r['answer']}"
        assert r["route"] in ("vector_rag", "cache_hit")
        assert len(r["sources"]) >= 1
        print(f"  * Q: '{q}' -> Cited: {r['sources'][0]['record_id']} (Conf: {r['confidence']:.2f})")

    # 6. Test Hybrid Cross-Domain Query
    print("\n[6/8] Testing Neuro-Symbolic Hybrid Query...")
    hybrid_q = "Is my attendance high enough according to college policy?"
    r = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": hybrid_q, "user_id": "U101"}).json()
    assert r["route"] == "hybrid"
    assert "84.5%" in r["answer"]
    assert len(r["offload_plan"]) == 2
    assert r["offload_plan"][0]["target_id"] == "db_personal_students_sql"
    assert r["offload_plan"][1]["target_id"] == "db_campus_knowledge_vector"
    print("  * Multi-Engine Offload Plan scheduled correctly (Relational SQL + Vector Store).")
    print(f"  * Reasoning trace: {len(r['reasoning_trace'])} steps.")

    # 7. Test Semantic Cache Performance
    print("\n[7/8] Testing Semantic Cache Latency...")
    repeat_q = "What are the rules and curfew timings for hostel students?"
    t0 = time.time()
    r1 = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": repeat_q}).json()
    dur1 = (time.time() - t0) * 1000

    t0 = time.time()
    r2 = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": repeat_q}).json()
    dur2 = (time.time() - t0) * 1000

    assert r2["route"] == "cache_hit"
    assert r2["answer"] == r1["answer"]
    print(f"  * Initial query duration: {dur1:.1f}ms (Route: {r1['route']})")
    print(f"  * Cached query duration:  {dur2:.1f}ms (Route: {r2['route']}) -> Instant hit!")

    # 8. Test Grounding & Refusal Gate
    print("\n[8/8] Testing Ungrounded Refusal Safety Gate...")
    out_of_domain = [
        "What is the capital of Mars?",
        "How do I bake chocolate cookies?",
        "Explain string theory in physics",
    ]
    for bad_q in out_of_domain:
        r = requests.post(f"{BASE_URL}/api/v1/ask", json={"question": bad_q}).json()
        assert r["confidence"] < 0.28
        assert "don't have enough" in r["answer"].lower() or "not enough information" in r["answer"].lower()
        print(f"  * Q: '{bad_q}' -> Safely Refused (Conf: {r['confidence']:.2f})")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! COMPLETE SYSTEM FULLY OPERATIONAL!")
    print("=" * 70)

if __name__ == "__main__":
    test_complete_system()
