import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DocumentRetriever:
    """
    Searches through FAQ/policy/course content.
    Uses TF-IDF (a classic, lightweight keyword-weighting technique)
    instead of a heavy embedding model, so it runs instantly with no
    downloads and stays well inside the RAM budget.
    """

    def __init__(self, documents_path="data/documents.json"):
        with open(documents_path) as f:
            self.documents = json.load(f)

        texts = [d["text"] for d in self.documents]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.doc_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=1):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.doc_matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for i in ranked[:top_k]:
            results.append({
                "record_id": self.documents[i]["id"],
                "source": self.documents[i]["source"],
                "snippet": self.documents[i]["text"],
                "score": float(scores[i]),
            })
        return results
