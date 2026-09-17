import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class DocumentRetriever:
    """
    Searches through FAQ/policy/course content using FAISS and sentence-transformers.
    """

    def __init__(self, index_path="data/faiss.index", meta_path="data/faiss_meta.json"):
        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path) as f:
                self.documents = json.load(f)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Failed to load FAISS index. Run ingestion.py first! {e}")
            self.index = None
            self.documents = []

    def search(self, query, top_k=1):
        if not self.index:
            return []
            
        query_vec = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vec, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "record_id": self.documents[idx]["id"],
                    "source": self.documents[idx]["source"],
                    "snippet": self.documents[idx]["text"],
                    "score": float(1.0 / (1.0 + distances[0][i])), # Convert L2 distance to a 0-1 confidence-like score
                })
        return results
