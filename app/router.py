import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

PERSONAL_KEYWORDS = [
    "my attendance", "my gpa", "my cgpa",
    "my grade", "my grades", "my semester", "my marks",
]

COMPLEX_KEYWORDS = [
    "summarize", "compare", "analyze", "explain in detail",
]

def classify_intent(question: str) -> str:
    """
    Neuro-symbolic router using rules + spaCy NLP to classify questions into:
    - personal: requires SQL lookup (e.g. my grades)
    - complex: requires LLM reasoning
    - common: standard FAQ/course content
    """
    q = question.lower()
    
    # 1. Rule-based checks
    if any(keyword in q for keyword in PERSONAL_KEYWORDS):
        return "personal"
        
    if any(keyword in q for keyword in COMPLEX_KEYWORDS):
        return "complex"
        
    # 2. NLP entity check for personal mentions
    doc = nlp(question)
    for token in doc:
        if token.dep_ == "poss" and token.text.lower() == "my":
            # "my [noun]" - likely personal data
            if token.head.pos_ == "NOUN":
                return "personal"

    return "common"
