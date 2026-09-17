# AMYPO Local Database Question-Answering System (MVP)

A self-hosted, offline Q&A system. No paid APIs. No internet dependency.

## What each file does

```
amypo-qa-system/
├── data_setup.py          <- run once: creates sample database + documents
├── requirements.txt       <- list of Python libraries needed
├── data/
│   ├── students.db        <- (auto-created) sample student records
│   └── documents.json     <- (auto-created) sample FAQ/policy/course text
└── app/
    ├── main.py             <- the FastAPI server (the "front door") - defines /api/v1/ask and /api/v1/health
    ├── router.py            <- decides: is this a personal question or a common one?
    ├── sql_engine.py        <- answers personal questions from the database
    ├── retrieval.py         <- searches FAQ/policy/course documents
    ├── cache.py             <- remembers answers to common questions
    ├── grounding.py         <- checks every answer has proof, or refuses
    └── models.py            <- defines the shape of requests/responses
```

## How to run this on your own computer (step by step)

### 1. Install Python (if you don't have it)
Download from https://python.org (version 3.10 or newer). During install, tick "Add Python to PATH".

### 2. Open a terminal in this folder
- Windows: open the `amypo-qa-system` folder, right-click inside it, choose "Open in Terminal"
- Mac/Linux: `cd path/to/amypo-qa-system`

### 3. Create a virtual environment (keeps things clean)
```bash
python -m venv venv
```
Activate it:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### 4. Install the required libraries
```bash
pip install -r requirements.txt
```

### 5. Create the sample data (run this once)
```bash
python data_setup.py
```
You should see:
```
[OK] Created data/students.db with sample records
[OK] Created data/documents.json with sample FAQ/policy/course content
```

### 6. Start the server
```bash
uvicorn app.main:app --reload
```
You should see:
```
Uvicorn running on http://127.0.0.1:8000
```
Leave this terminal window open — it's your running server.

### 7. Test it!

**Option A — Browser (easiest):**
Open http://127.0.0.1:8000/docs in your browser. This is an auto-generated interactive test page.
Click on `POST /api/v1/ask` → "Try it out" → type a question → "Execute".

**Option B — curl (in a second terminal):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ask -H "Content-Type: application/json" -d "{\"question\":\"What time does the library open?\"}"
```

## Sample questions to try

| Question | user_id | What happens |
|---|---|---|
| "What is my attendance?" | S101 | Looks up SQL database, always fresh |
| "What time does the library open?" | (none) | Searches documents, then caches the answer |
| "What does Module 3 of DBMS cover?" | (none) | Searches course content |
| "What is the capital of France?" | (none) | Refuses — no grounded source found |

Try `student_id` values: `S101`, `S102`, `S103` (see `data_setup.py` for their records).

## How a question flows through the system

1. Your question hits `app/main.py` → `POST /api/v1/ask`
2. `router.py` decides: does this look like a **personal** question (contains "my attendance", "my gpa", etc.) or a **common** one?
3. If personal → `sql_engine.py` looks it up directly in `students.db` (always fresh, never cached)
4. If common → `cache.py` checks if we've answered something very similar before
   - If yes → instant answer, no searching needed
   - If no → `retrieval.py` searches `documents.json` for the most relevant passage
5. Either way, `grounding.py` checks: is there actually a source backing this answer, and is confidence high enough?
   - If yes → return the answer + source citation
   - If no → honestly say "I don't have enough information"

## What's simplified for this MVP (be upfront about this)

- **No LLM phrasing yet** — answers are extracted directly from the source text rather than reworded by a language model. This is a deliberate choice: it guarantees zero hallucination for the demo. The next step is adding a local model (e.g. Ollama + Phi-3-mini) to phrase answers more naturally while still only using the retrieved text as its source.
- **TF-IDF instead of embeddings** — a simpler, classic retrieval technique. It works well for small document sets and needs no model download. A full version would use sentence-transformers + FAISS for better semantic matching.
- **In-memory cache** — resets when the server restarts. A production version would persist it to disk.

## Next steps to extend this into the full system

1. Add Ollama + a small local model to phrase answers instead of returning raw text.
2. Swap TF-IDF for sentence-transformers + FAISS for smarter semantic search.
3. Build the Next.js chat UI to replace the `/docs` testing page.
4. Add more sample data and run it against the official benchmark Q&A set.
5. Tune the `CONFIDENCE_THRESHOLD` in `grounding.py` against real results.
