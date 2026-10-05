import json
import os
from typing import Any, Dict, Optional
import requests
from app.router.schemas import RouteType

OLLAMA_BASE = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"
ROUTER_MODEL = os.getenv("ROUTER_SLM_MODEL", "phi4-mini")
TIMEOUT_SECONDS = float(os.getenv("ROUTER_SLM_TIMEOUT", "3.0"))


SYSTEM_PROMPT = """You are an ultra-fast, deterministic Neuro-Symbolic Query Router for an institutional Hybrid QA system.
Your job is to classify the user's intent and output a strict JSON object with no preamble, markdown ticks, or surrounding explanation.

Routing Categories:
- "personal_sql": Queries about the individual user's personal private data (e.g., their own attendance, grades, GPA, marks, balance, profile).
- "vector_rag": Queries about campus policies, course curriculum, schedules, library timings, professor details, general FAQ, or general factual questions.
- "hybrid": Queries requiring BOTH personal metrics AND public rules to answer (e.g., "Is my attendance high enough for the final exam?").
- "direct_answer": ONLY explicit conversational greetings and small talk (e.g., "hello", "hi", "good morning", "thank you").

JSON Output Schema:
{
  "route": "personal_sql" | "vector_rag" | "hybrid" | "direct_answer",
  "confidence": float (0.0 to 1.0),
  "intent_summary": "one sentence explanation",
  "sql_subquery": "extracted personal data query or null",
  "rag_subquery": "extracted public knowledge query or null"
}
"""

FEW_SHOT_EXAMPLES = [
    {
        "query": "What is my current CGPA for semester 3?",
        "output": {
            "route": "personal_sql",
            "confidence": 0.99,
            "intent_summary": "User wants their specific CGPA for semester 3.",
            "sql_subquery": "Retrieve CGPA for semester 3",
            "rag_subquery": None
        }
    },
    {
        "query": "What is the minimum attendance required to appear for semester exams?",
        "output": {
            "route": "vector_rag",
            "confidence": 0.98,
            "intent_summary": "Inquiring about institutional exam attendance policy.",
            "sql_subquery": None,
            "rag_subquery": "minimum attendance requirement for semester exams"
        }
    },
    {
        "query": "Is my 72% attendance enough to sit for the finals according to college policy?",
        "output": {
            "route": "hybrid",
            "confidence": 0.96,
            "intent_summary": "Comparing user's personal attendance with college policy requirements.",
            "sql_subquery": "Retrieve user attendance percentage",
            "rag_subquery": "college policy minimum attendance criteria for finals"
        }
    },
    {
        "query": "what is my attendane",
        "output": {
            "route": "personal_sql",
            "confidence": 0.98,
            "intent_summary": "User is inquiring about their personal attendance record (typo corrected).",
            "sql_subquery": "Retrieve attendance percentage",
            "rag_subquery": None
        }
    },
    {
        "query": "how much attendance do i have",
        "output": {
            "route": "personal_sql",
            "confidence": 0.98,
            "intent_summary": "User checking personal attendance status.",
            "sql_subquery": "Retrieve attendance percentage",
            "rag_subquery": None
        }
    }
]


class NeuroRouterEngine:
    """
    SLM/LLM-backed neuro router that provides deep semantic understanding
    and JSON schema enforcement for complex, typo-laden, or boundary cases.
    """

    def __init__(self, model_name: str = ROUTER_MODEL, base_url: str = OLLAMA_URL):
        self.model_name = model_name
        self.base_url = base_url

    def classify_with_slm(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Sends query to the local LLM/SLM with constrained JSON format prompt.
        Prioritizes:
          1. Local in-process GGUF model (Qwen2.5-1.5B)
          2. Ollama REST endpoint
          3. Deterministic semantic intent fallback
        """
        # 1. Try local in-process GGUF model first if available
        gguf_res = self._try_local_gguf(query)
        if gguf_res:
            return gguf_res

        # 2. Try local Ollama if available
        ollama_res = self._try_ollama(query)
        if ollama_res:
            return ollama_res

        # 3. Robust deterministic semantic fallback
        return self._semantic_fallback(query)

    def _try_local_gguf(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            from app.llm_engine import get_local_llama
            llm = get_local_llama()
            if not llm:
                return None

            prompt_user = f"Query: {query}\nOutput JSON:"
            prompt = (
                f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
                f"<|im_start|>user\n{prompt_user}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            output = llm(
                prompt,
                max_tokens=120,
                temperature=0.0,
                top_p=0.1,
                stop=["<|im_end|>", "\n\nQuery:"],
            )
            raw_text = output["choices"][0]["text"].strip()
            return self._parse_json_result(raw_text, model_name="local-gguf-qwen2.5", query=query)
        except Exception:
            return None

    def _try_ollama(self, query: str) -> Optional[Dict[str, Any]]:
        prompt = f"{SYSTEM_PROMPT}\n\nExamples:\n"
        for ex in FEW_SHOT_EXAMPLES:
            prompt += f"Query: {ex['query']}\nOutput: {json.dumps(ex['output'])}\n\n"
        prompt += f"Query: {query}\nOutput:"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.0, "top_p": 0.1, "num_predict": 128},
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=TIMEOUT_SECONDS)
            if response.status_code == 200:
                data = response.json()
                raw_text = data.get("response", "").strip()
                return self._parse_json_result(raw_text, model_name=self.model_name, query=query)
        except Exception:
            return None
        return None

    @staticmethod
    def _is_actual_greeting(query: str) -> bool:
        q = query.lower().strip().rstrip("!.? ")
        return q in {
            "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
            "how are you", "who are you", "what can you do", "thanks", "thank you", "bye", "goodbye"
        } or any(q.startswith(g) for g in ["hi ", "hello ", "hey ", "greetings"])

    def _parse_json_result(self, raw_text: str, model_name: str, query: str = "") -> Optional[Dict[str, Any]]:
        try:
            # Strip markdown json blocks if present
            clean = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)

            route_str = parsed.get("route", "").lower()
            if "sql" in route_str or "personal" in route_str:
                route = RouteType.SQL
            elif "hybrid" in route_str:
                route = RouteType.HYBRID
            elif "direct" in route_str or "chitchat" in route_str:
                route = RouteType.CHITCHAT if (query and self._is_actual_greeting(query)) else RouteType.RAG
            elif "rag" in route_str or "vector" in route_str:
                route = RouteType.RAG
            else:
                route = RouteType.UNKNOWN

            return {
                "route": route,
                "confidence": float(parsed.get("confidence", 0.95)),
                "intent_summary": parsed.get("intent_summary", "SLM intent classification"),
                "sql_subquery": parsed.get("sql_subquery"),
                "rag_subquery": parsed.get("rag_subquery"),
                "model_used": model_name,
            }
        except Exception:
            return None

    def _semantic_fallback(self, query: str) -> Dict[str, Any]:
        """High-accuracy fallback parsing intent even with typos and slang."""
        q_lower = query.lower()

        # Check for personal intent keywords or typos (attendane, mrks, grad, etc.)
        has_personal_pronoun = any(p in q_lower for p in ["my", "mine", "for me", "what about me", "i have", "am i", "who am i"])
        has_attendance = any(w in q_lower for w in ["attendance", "attendane", "attendence", "atendance", "attndance", "present", "absent"])
        has_grades = any(w in q_lower for w in ["gpa", "cgpa", "sgpa", "grade", "grades", "marks", "mrks", "score"])
        has_policy = any(w in q_lower for w in ["policy", "rule", "rules", "regulation", "eligib", "criteria", "minimum", "threshold"])

        if (has_attendance or has_grades) and has_policy:
            return {
                "route": RouteType.HYBRID,
                "confidence": 0.95,
                "intent_summary": "Evaluating personal metrics against institutional policy requirements.",
                "sql_subquery": query,
                "rag_subquery": query,
                "model_used": "semantic-heuristic-refiner",
            }
        elif has_personal_pronoun or has_attendance or has_grades:
            return {
                "route": RouteType.SQL,
                "confidence": 0.95,
                "intent_summary": "Personal relational query targeting user records (typo-tolerant intent).",
                "sql_subquery": query,
                "rag_subquery": None,
                "model_used": "semantic-heuristic-refiner",
            }
        elif has_policy or any(w in q_lower for w in ["library", "hostel", "mess", "bus", "schedule", "calendar", "fee structure"]):
            return {
                "route": RouteType.RAG,
                "confidence": 0.92,
                "intent_summary": "Institutional knowledge inquiry.",
                "sql_subquery": None,
                "rag_subquery": query,
                "model_used": "semantic-heuristic-refiner",
            }
        return {
            "route": RouteType.RAG,
            "confidence": 0.70,
            "intent_summary": "General campus inquiry.",
            "sql_subquery": None,
            "rag_subquery": query,
            "model_used": "semantic-heuristic-refiner",
        }
