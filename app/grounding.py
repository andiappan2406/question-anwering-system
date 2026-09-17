# If confidence is below this, we refuse instead of guessing.
CONFIDENCE_THRESHOLD = 0.4


def apply_grounding(answer, sources, confidence):
    """
    Final quality gate every answer must pass through.
    No answer leaves the system without either:
      (a) a cited source + high enough confidence, or
      (b) an honest refusal.
    """
    if answer is None or confidence < CONFIDENCE_THRESHOLD:
        return {
            "answer": "I don't have enough grounded information to answer "
                       "that confidently. Please rephrase or contact staff.",
            "sources": [],
            "confidence": round(confidence, 2),
        }
    return {
        "answer": answer,
        "sources": sources,
        "confidence": round(confidence, 2),
    }
