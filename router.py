# Symbolic rule layer: fast, explainable, zero model-inference cost.
# If a question mentions "my ..." + a personal-data keyword, it's personal.
# Everything else is treated as a common/FAQ/course question.

PERSONAL_KEYWORDS = [
    "my attendance", "my gpa", "my cgpa",
    "my grade", "my grades", "my semester", "my marks",
]


def classify_intent(question: str) -> str:
    q = question.lower()
    if any(keyword in q for keyword in PERSONAL_KEYWORDS):
        return "personal"
    return "common"
