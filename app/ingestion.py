import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def ingest_documents(documents_path="data/documents.json", index_path="data/faiss.index", meta_path="data/faiss_meta.json"):
    print(f"Loading documents from {documents_path}...")
    with open(documents_path) as f:
        documents = json.load(f)
        
    texts = [d["text"] for d in documents]
    
    print("Loading embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Encoding texts...")
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    print(f"Saving FAISS index to {index_path}...")
    faiss.write_index(index, index_path)
    
    print(f"Saving metadata to {meta_path}...")
    with open(meta_path, 'w') as f:
        json.dump(documents, f)
        
    print("Ingestion complete.")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    ingest_documents()
