import numpy as np

class SemanticCache:
    """
    Caches answers ONLY for common/FAQ/course questions.
    Personal data queries never touch this -- they are always
    answered fresh from the database (see sql_engine.py).
    """

    def __init__(self, model, similarity_threshold=0.85):
        self.model = model
        self.threshold = similarity_threshold
        self.entries = []  # each: {vector, question, answer, sources, confidence}

    def _cosine_similarity(self, v1, v2):
        dot = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot / (norm_v1 * norm_v2)

    def lookup(self, question):
        if not self.entries or not self.model:
            return None
        query_vec = self.model.encode([question], convert_to_numpy=True)[0]
        for entry in self.entries:
            sim = self._cosine_similarity(query_vec, entry["vector"])
            if sim >= self.threshold:
                return entry
        return None

    def store(self, question, answer, sources, confidence):
        if not self.model:
            return
        vector = self.model.encode([question], convert_to_numpy=True)[0]
        self.entries.append({
            "vector": vector,
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        })
