import os
import re
import requests
import json
from typing import Optional

# ── Local GGUF model ─────────────────────────────────────────────────────────
DEFAULT_GGUF_PATH = "/media/ank/win_user_datas/proj/Projects/AiDevSpeaker/models/Qwen2.5-1.5B-Instruct/qwen2.5-1.5b-instruct-q8_0.gguf"
GGUF_MODEL_PATH = os.getenv("LOCAL_GGUF_MODEL_PATH", DEFAULT_GGUF_PATH)

# ── Ollama fallback ──────────────────────────────────────────────────────────
OLLAMA_BASE = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"
SLM_MODEL = os.getenv("SLM_MODEL", "phi3")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

_llama_instance = None

# Detect raw-snippet pass-through so we can substitute a proper response
_RAW_SNIPPET_MARKERS = ["small talk", "saying hello", "making small talk"]

SYSTEM_PROMPT = (
    "You are an AI assistant for an institutional campus Q&A system called AMYPO. "
    "Answer the user's question accurately using ONLY the provided text snippet. "
    "Keep your answer clear, polite, and fully informative. "
    "Always preserve all specific names, ID numbers, percentages, grades, courses, and standing from the snippet. "
    "Never truncate into just a single word or bare number without context. "
    "Do not make up outside facts."
)

CHITCHAT_REPLIES = [
    "Hello! I'm the AMYPO campus assistant. How can I help you today?",
    "Hi there! What would you like to know about AMYPO?",
    "Hey! Ask me anything about campus policies, courses, or your student records.",
]


def get_local_llama():
    """Lazy singleton loader for in-process GGUF model via llama-cpp."""
    global _llama_instance
    if _llama_instance is None and os.path.exists(GGUF_MODEL_PATH):
        try:
            from llama_cpp import Llama
            print(f"[LLM Engine] Loading GGUF model: {GGUF_MODEL_PATH}")
            _llama_instance = Llama(
                model_path=GGUF_MODEL_PATH,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=-1,  # offload all layers to GPU
                verbose=False,
            )
            print("[LLM Engine] Local GGUF model loaded successfully!")
        except Exception as e:
            print(f"[LLM Engine] Failed to load local GGUF: {e}")
            _llama_instance = None
    return _llama_instance


def _try_local_gguf(question: str, raw_snippet: str, is_complex: bool) -> Optional[str]:
    """Try inference using the local GGUF model."""
    llm = get_local_llama()
    if llm is None:
        return None
    try:
        user_msg = f"Question: {question}\n\nRelevant Information:\n{raw_snippet}\n\nAnswer:"
        prompt = (
            f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{user_msg}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        output = llm(
            prompt,
            max_tokens=300,
            temperature=0.2,
            top_p=0.9,
            stop=["<|im_end|>", "\n\nUser:", "Question:"],
        )
        generated = output["choices"][0]["text"].strip()
        return generated if generated else None
    except Exception as e:
        print(f"[LLM Engine] GGUF inference error: {e}")
        return None


def _try_ollama(question: str, raw_snippet: str, is_complex: bool) -> Optional[str]:
    """Try inference via local Ollama endpoint."""
    model = LLM_MODEL if is_complex else SLM_MODEL
    prompt = (
        f"You are an AI assistant for a campus Q&A system (AMYPO).\n"
        f"Answer using ONLY the provided snippet. Be concise and direct.\n\n"
        f"Question: {question}\n\nSnippet: {raw_snippet}\n\nAnswer:"
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            generated = data.get("response", "").strip()
            return generated if generated else None
    except Exception:
        pass
    return None


def rephrase_answer(question: str, raw_snippet: str, is_complex: bool = False) -> str:
    """
    Synthesizes a conversational answer using:
      1. Local in-process GGUF model (GPU accelerated)
      2. Local Ollama endpoint (fallback)
      3. Raw snippet (final fallback)

    Also guards against the LLM returning the raw snippet pass-through text.
    """
    # Guard: if raw_snippet is a chitchat placeholder, return a real greeting
    if any(marker in raw_snippet for marker in _RAW_SNIPPET_MARKERS):
        return CHITCHAT_REPLIES[0]

    result = _try_local_gguf(question, raw_snippet, is_complex)
    if result and not any(marker in result for marker in _RAW_SNIPPET_MARKERS):
        if len(result.strip()) < 25 and len(raw_snippet.strip()) >= 35:
            return raw_snippet
        return result

    result = _try_ollama(question, raw_snippet, is_complex)
    if result and not any(marker in result for marker in _RAW_SNIPPET_MARKERS):
        if len(result.strip()) < 25 and len(raw_snippet.strip()) >= 35:
            return raw_snippet
        return result

    # Final fallback: return raw snippet as-is
    return raw_snippet
