import re
from typing import Dict, List, Optional, Set, Tuple
import spacy
from app.router.schemas import DataPriority, RouteType

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Personal fields & entities typically residing in relational user/student databases (including common typos)
PERSONAL_FIELDS: Dict[str, List[str]] = {
    "attendance": [
        "attendance", "attendane", "attendence", "atendance", "attndance", "attendace", "attandance",
        "attendence percentage", "attendane percentage", "present", "absent", "attendance percentage",
        "classes attended", "how much attendance", "my attendance", "my attendane", "my attendence"
    ],
    "gpa": ["gpa", "cgpa", "sgpa", "grade point", "grade point average", "gpa score"],
    "grades": ["grade", "grades", "marks", "mrks", "score", "scores", "result", "results", "transcript"],
    "semester": ["semester", "term", "current semester", "enrolled semester", "academic year"],
    "profile": ["student id", "roll number", "email", "phone", "profile", "registered courses", "my name", "who am i", "my details", "my info", "profle", "identity"],
    "financials": ["fee", "fees", "dues", "balance", "scholarship status", "payment", "tuition fee"],
    "department": ["department", "branch", "major", "stream"],
    "mentor": ["mentor", "advisor", "faculty advisor", "counselor", "guide"],
    "hostel": ["hostel", "hostel room", "my room", "accommodation", "stay", "bus route", "day scholar"],
    "courses": ["course", "courses", "subject", "subjects", "registered courses", "enrolled courses", "my classes"],
    "office": ["office", "office room", "my office", "cabin", "my cabin", "my desk"],
    "role": ["role", "designation", "my role", "my designation", "position", "my title"],
    "specialization": ["specialization", "research area", "my specialization", "my research"],
    "teaching": ["courses i teach", "subjects i teach", "classes i teach", "my teaching", "what do i teach"],
    "skills": ["skill", "skills", "tech stack", "technologies", "projects", "certifications", "placement profile"],
}

# General knowledge / public policy topics typically residing in vector stores / documentation
COMMON_KNOWLEDGE_TOPICS: List[str] = [
    "policy", "rule", "rules", "regulation", "regulations", "criteria", "eligibility",
    "syllabus", "curriculum", "calendar", "schedule", "deadline", "holiday", "holidays",
    "timing", "timings", "hours", "contact", "faculty", "professor", "hostel", "library",
    "mess", "canteen", "bus", "transport", "placement", "internship", "admission",
    "minimum requirement", "grading system", "passing mark", "dean",
    # Staff / department
    "head", "hod", "head of department", "cse", "department", "staff", "lecturer",
    "assistant professor", "principal", "vice principal",
    # Campus facilities
    "lab", "laboratory", "workshop", "cafeteria", "sports", "gym", "clinic", "health center",
    "wifi", "internet", "club", "event", "fest", "technova", "aura", "amypo", "college", "institution",
    # Course / exam
    "exam", "examination", "arrear", "retake", "fee", "fees", "scholarship",
    "module", "unit", "subject", "course", "class", "lecture", "dbms",
]

# Comparative / cross-domain connector phrases that signal a hybrid query
HYBRID_CONNECTORS: List[str] = [
    "compared to", "compared with", "as per", "according to", "eligible for",
    "qualify for", "meet the requirement", "meets the requirement", "versus", "vs",
    "relative to", "threshold", "minimum required", "is enough for", "am i allowed",
    "can i apply", "can i write", "can i attend", "do i qualify", "am i eligible",
    "is my attendance enough", "is my gpa enough",
]

# Analytical / Aggregation indicators
AGGREGATION_KEYWORDS: Set[str] = {
    "average", "avg", "total", "sum", "highest", "lowest", "max", "min", "count", "rank"
}

# Conversational Greeting keywords
GREETINGS: Set[str] = {
    "hi", "hello", "hey", "who are you", "what are you", "how are you",
    "good morning", "good evening", "good afternoon", "hi there", "hello there",
    "what can you do", "help me", "help", "start", "thanks", "thank you",
    "bye", "goodbye", "see you", "ok", "okay", "sure", "alright",
}


class SymbolicGatekeeper:
    """
    High-speed, zero-hallucination symbolic analyzer that uses tokenization,
    part-of-speech dependency trees, and keyword taxonomy to classify queries
    and extract structured parameters.
    """

    def __init__(self):
        self.nlp = nlp

    def analyze(self, query: str) -> Dict:
        """
        Executes symbolic analysis over the user query.
        Returns a dictionary with route classification, matched fields,
        extracted parameters, and sub-queries.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()
        doc = self.nlp(q_clean)

        matched_personal_fields: List[str] = []
        has_personal_pronoun = False
        has_common_topic = False
        has_hybrid_connector = False
        has_aggregation = False

        # 1. Dependency Tree & POS check for personal possession ("my X", "our Y", "I have")
        for token in doc:
            if token.dep_ == "poss" and token.text.lower() in {"my", "our", "mine"}:
                if token.head.pos_ in {"NOUN", "PROPN"}:
                    has_personal_pronoun = True
            if token.text.lower() in {"i", "me", "myself"} and token.dep_ in {"nsubj", "dobj", "pobj"}:
                # Exclude informational command verbs where 'me' is just the listener (e.g. 'tell me about X', 'show me Y')
                if token.head.lemma_.lower() in {"tell", "show", "give", "help", "explain", "inform", "guide", "brief"}:
                    continue
                has_personal_pronoun = True

        # Explicit personal phrase triggers
        if any(p in q_lower for p in ["who am i", "my name", "my id", "my profile", "my details"]):
            has_personal_pronoun = True

        # 2. Check personal field taxonomy
        for field_key, aliases in PERSONAL_FIELDS.items():
            for alias in aliases:
                if re.search(r"\b" + re.escape(alias) + r"\b", q_lower):
                    matched_personal_fields.append(field_key)
                    break

        # If personal keywords appear with "my" or "i"
        if re.search(
            r"\bmy\s+(attendance|gpa|cgpa|grade|grades|marks|score|semester|fee|fees|dues|balance|profile|name|id|department|branch|mentor|advisor|room|hostel|details|email|courses|subjects|classes)\b",
            q_lower,
        ):
            has_personal_pronoun = True

        # 3. Check common knowledge topic taxonomy
        matched_common_topics = []
        for topic in COMMON_KNOWLEDGE_TOPICS:
            if re.search(r"\b" + re.escape(topic) + r"\b", q_lower):
                has_common_topic = True
                matched_common_topics.append(topic)

        # 4. Check hybrid connectors
        for connector in HYBRID_CONNECTORS:
            if connector in q_lower:
                has_hybrid_connector = True
                break

        # Check hybrid intent keywords
        has_hybrid_intent = has_hybrid_connector or any(
            w in q_lower for w in ["eligible", "eligibility", "qualify", "allowed", "can i", "enough for", "criteria"]
        )

        # 5. Check aggregation keywords
        for word in q_lower.split():
            if word in AGGREGATION_KEYWORDS:
                has_aggregation = True
                break

        # Routing decision logic
        sql_subquery: Optional[str] = None
        rag_subquery: Optional[str] = None

        is_greeting = q_lower in GREETINGS or bool(re.match(r"^(hi+|hello+|hey+|hola|greetings)\b", q_lower))

        # Determine personal intent: requires personal field or explicit identity phrase
        has_explicit_personal_phrase = any(
            p in q_lower for p in [
                "who am i", "my name", "my id", "my profile", "my details",
                "tell me my details", "show my details", "for me", "what about me",
                "and for me", "mine", "how about me", "tell me about me"
            ]
        )
        is_policy_rule_query = any(
            p in q_lower for p in [
                "policy", "rule", "rules", "regulation", "regulations", "criteria",
                "condonation policy", "minimum required", "cut off", "concession",
                "procedure", "how to apply", "guideline", "guidelines"
            ]
        )
        is_personal = (
            has_explicit_personal_phrase
            or (has_personal_pronoun and len(matched_personal_fields) > 0)
            or (len(matched_personal_fields) > 0 and not is_policy_rule_query)
        )

        is_placement_matching = any(
            p in q_lower for p in [
                "suggest student", "suggest students", "recommend student", "recommend students",
                "candidates for", "students for", "who matches", "who is suitable", "best match for",
                "who should we select", "selection for company", "skill and role get match",
                "role for me", "roles for me", "job for me", "jobs for me", "openings for me",
                "match my skills", "match my profile", "which company should i apply",
                "all company openings", "list openings", "what companies are hiring",
                "student suggestion", "student suggestions"
            ]
        ) or (
            any(comp in q_lower for comp in ["google", "microsoft", "amazon", "zoho", "bosch", "l&t", "tcs", "razorpay"])
            and any(w in q_lower for w in ["student", "students", "candidate", "candidates", "recommend", "suggest", "select", "hire", "opening", "role", "match"])
        )

        if is_greeting:
            primary_route = RouteType.CHITCHAT
            confidence = 1.0
            intent = "Conversational greeting or small talk."
            sql_subquery = None
            rag_subquery = None

        elif is_placement_matching:
            primary_route = RouteType.SQL
            confidence = 0.98
            intent = "Placement skill-to-role matching query evaluating company requirements against student skill profiles."
            sql_subquery = q_clean
            rag_subquery = None

        elif is_personal and has_hybrid_intent:
            # Hybrid query: combines personal metric with institutional policy evaluation
            primary_route = RouteType.HYBRID
            confidence = 0.95
            intent = "Cross-domain query comparing personal database metrics with institutional knowledge."
            sql_subquery = f"Retrieve user records for {', '.join(set(matched_personal_fields)) or 'profile'}."
            rag_subquery = ", ".join(set(matched_common_topics)) if matched_common_topics else query

        elif is_personal:
            # Pure personal SQL query
            primary_route = RouteType.SQL
            confidence = 0.98 if has_personal_pronoun else 0.88
            intent = f"Personal relational database query targeting fields: {set(matched_personal_fields) or 'user record'}."
            sql_subquery = q_clean

        elif has_personal_pronoun and not is_policy_rule_query:
            # Personal query with typo or unusual phrasing (e.g. "what is my attendane")
            primary_route = RouteType.SQL
            confidence = 0.75
            intent = "Personal user query with personal pronoun requiring intent verification."
            sql_subquery = q_clean

        elif has_common_topic:
            # Institutional RAG query with matched policy topic
            primary_route = RouteType.RAG
            confidence = 0.92
            intent = f"Knowledge base / FAQ vector search on topics: {set(matched_common_topics) or 'general FAQ'}."
            rag_subquery = q_clean

        elif len(q_clean.split()) >= 2:
            # Borderline query: confidence < 0.90 so Neuro SLM can examine user need
            primary_route = RouteType.RAG
            confidence = 0.65
            intent = "General institutional query requiring semantic understanding."
            rag_subquery = q_clean

        else:
            primary_route = RouteType.UNKNOWN
            confidence = 0.40
            intent = "Ambiguous or short query requiring further refinement."

        return {
            "primary_route": primary_route,
            "confidence": confidence,
            "intent_summary": intent,
            "has_personal_pronoun": has_personal_pronoun,
            "matched_personal_fields": list(set(matched_personal_fields)),
            "matched_common_topics": list(set(matched_common_topics)),
            "has_hybrid_connector": has_hybrid_connector,
            "has_aggregation": has_aggregation,
            "sql_subquery": sql_subquery,
            "rag_subquery": rag_subquery,
            "reasoning": [
                f"Symbolic POS check: personal_pronoun={has_personal_pronoun}",
                f"Fields matched: {list(set(matched_personal_fields))}",
                f"Common topics matched: {list(set(matched_common_topics))}",
                f"Hybrid indicator: {has_hybrid_intent}",
                f"Route assigned: {primary_route.value} (confidence={confidence})"
            ]
        }
