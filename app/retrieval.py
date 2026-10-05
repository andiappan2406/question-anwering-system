import json
import faiss
import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class FastEmbedWrapper:
    """
    Lightweight ONNX-based embedding wrapper (no PyTorch needed).
    Always returns L2-normalized vectors so that IndexFlatIP == cosine similarity.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model = TextEmbedding(model_name=model_name)

    def encode(self, texts, convert_to_numpy: bool = True):
        embeddings = list(self.model.embed(texts))
        arr = np.array(embeddings, dtype=np.float32)
        # Normalize so that inner product = cosine similarity
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / np.where(norms == 0, 1e-10, norms)
        return arr if convert_to_numpy else arr.tolist()


class DocumentRetriever:
    """
    Searches through FAQ/policy/course content using FAISS + fastembed (lightweight ONNX).
    Uses cosine similarity via IndexFlatIP with L2-normalized vectors.
    """

    def __init__(
        self,
        index_path: str = "data/faiss.index",
        meta_path: str = "data/faiss_meta.json",
    ):
        self.index = None
        self.documents = []
        self.model = FastEmbedWrapper(MODEL_NAME)
        try:
            self.index = faiss.read_index(index_path)
            with open(meta_path) as f:
                self.documents = json.load(f)
            print(f"[Retriever] Loaded {len(self.documents)} documents from FAISS index.")
        except Exception as e:
            print(f"[Retriever] Warning: Could not load FAISS index — {e}")
            print("[Retriever] Run `python app/ingestion.py` to build the index.")

    def search(self, query: str, top_k: int = 2, min_score: float = 0.38):
        """
        Search for the top_k most semantically similar documents.
        Returns empty list if best score is below min_score.
        """
        if self.index is None or not self.documents:
            return []

        query_vec = self.model.encode([query], convert_to_numpy=True)
        # scores are cosine similarity values in range [-1, 1]
        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            score = float(scores[0][i])
            if score < min_score:
                continue  # Skip results below the relevance threshold
            results.append({
                "record_id": self.documents[idx]["id"],
                "source": self.documents[idx]["source"],
                "snippet": self.documents[idx]["text"],
                "score": round(score, 4),
            })
        return results
