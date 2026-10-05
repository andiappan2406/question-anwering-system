"""
Run this ONCE before starting the server (or when documents.json changes).
Rebuilds the FAISS vector index using fastembed (lightweight ONNX, no PyTorch needed).
"""
import json
import os
import faiss
import numpy as np
from fastembed import TextEmbedding


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def ingest_documents(
    documents_path: str = "data/documents.json",
    index_path: str = "data/faiss.index",
    meta_path: str = "data/faiss_meta.json",
):
    print(f"Loading documents from {documents_path}...")
    with open(documents_path) as f:
        documents = json.load(f)

    texts = [d["text"] for d in documents]

    print(f"Loading fastembed model ({MODEL_NAME})...")
    model = TextEmbedding(model_name=MODEL_NAME)

    print("Encoding texts...")
    embeddings_gen = model.embed(texts)
    embeddings = np.array(list(embeddings_gen), dtype=np.float32)

    # Normalize vectors so that Inner Product == Cosine Similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.where(norms == 0, 1e-10, norms)

    dimension = embeddings.shape[1]
    # IndexFlatIP with normalized vectors = exact cosine similarity search
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    print(f"Saving FAISS index to {index_path}...")
    faiss.write_index(index, index_path)

    print(f"Saving metadata to {meta_path}...")
    with open(meta_path, "w") as f:
        json.dump(documents, f, indent=2)

    print(f"Ingestion complete. Indexed {len(documents)} documents.")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    ingest_documents()
