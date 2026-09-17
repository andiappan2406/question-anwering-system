import requests
import json

import os

# Local Ollama endpoint
OLLAMA_BASE = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"

# SLM (Small Language Model) for routine queries
SLM_MODEL = "phi3"
# LLM fallback for complex queries
LLM_MODEL = "llama3"

def rephrase_answer(question: str, raw_snippet: str, is_complex: bool = False) -> str:
    """
    Sends the raw snippet and the question to the local Ollama instance
    to generate a natural, conversational response.
    Routes to a larger LLM if is_complex is True, otherwise uses the SLM.
    """
    model = LLM_MODEL if is_complex else SLM_MODEL
    
    prompt = f"""You are an AI assistant for a campus Q&A system. 
Your task is to answer the user's question using ONLY the provided text snippet.
Keep your answer brief, conversational, and direct. Do not add outside information.

Question: {question}

Snippet: {raw_snippet}
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        return raw_snippet
    except Exception as e:
        print(f"Local Ollama API Error ({model}): {e}")
        return raw_snippet
