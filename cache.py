from sklearn.metrics.pairwise import cosine_similarity


class SemanticCache:
    """
    Caches answers ONLY for common/FAQ/course questions.
    Personal data queries never touch this -- they are always
    answered fresh from the database (see sql_engine.py).
    """

    def __init__(self, vectorizer, similarity_threshold=0.85):
        self.vectorizer = vectorizer
        self.threshold = similarity_threshold
        self.entries = []  # each: {vector, question, answer, sources, confidence}

    def lookup(self, question):
        if not self.entries:
            return None
        query_vec = self.vectorizer.transform([question])
        for entry in self.entries:
            sim = cosine_similarity(query_vec, entry["vector"])[0][0]
            if sim >= self.threshold:
                return entry
        return None

    def store(self, question, answer, sources, confidence):
        vector = self.vectorizer.transform([question])
        self.entries.append({
            "vector": vector,
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        })
