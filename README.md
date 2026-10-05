# AMYPO Local Neuro-Symbolic Hybrid Question-Answering System

A high-performance, institutional, self-hosted Neuro-Symbolic Hybrid Q&A system for campus knowledge, official academic policies, and confidential student records.

- **Versatile Dual-Dialect Database Manager**: Production connection to **Supabase PostgreSQL** cloud instance with connection pooling, automated table auto-migration, seed synchronization, and zero-config local **SQLite** fallback.
- **Placement & Role Matching Engine**: Replaces random recruitment allocation with deterministic skill-to-role matching (60% skill fit, 25% GPA, 15% attendance), skill gap diagnostics, and eligibility checks.
- **Zero External API Cost**: Runs locally with offline embeddings (FastEmbed ONNX), FAISS vector store, multi-dialect SQL engine, and local SLM inference.
- **Neuro-Symbolic Gatekeeper**: Fast deterministic linguistic parsing (spaCy dependency trees + taxonomy) coupled with local Small Language Model (SLM) reasoning for complex boundary cases.
- **Structured Database Offload Planning**: Deterministic offload planning across relational SQL (`students`, `staff`, `courses`, `company_openings`, `student_skills`), vector knowledge store, and semantic cache with strict priority ordering (`CRITICAL` -> `HIGH` -> `MEDIUM` -> `LOW`).
- **Grounded & Auditable**: Hard confidence thresholding, source attribution with relevance scoring, and step-by-step reasoning traces.
- **Modern Next.js Web Interface**: Interactive chat workstation with live route badges, expandable neuro-symbolic reasoning & offload plan drawers, live database status badge, and interactive placement matcher modal.

---

## Architecture & Directory Layout

```
Database-Q-A-system/
├── app/
│   ├── db_manager.py             <- Versatile Multi-Dialect Manager (Supabase PostgreSQL + SQLite)
│   ├── placement_engine.py       <- Deterministic Skill-to-Role & Candidate Matching Engine
│   ├── router/                   <- Modular Neuro-Symbolic Routing Engine
│   │   ├── __init__.py           <- Public interface & backwards-compatible classify_intent
│   │   ├── schemas.py            <- RouteType, OffloadTarget, HealthStatus, CandidateMatch schemas
│   │   ├── symbolic.py           <- High-speed spaCy gatekeeper & linguistic taxonomy
│   │   ├── neuro.py              <- SLM (Ollama) semantic verification & JSON formatting
│   │   ├── offloader.py          <- Database registry & multi-engine offload planner
│   │   ├── sorter.py             <- Production context sorting hierarchy (Priority -> Score -> Time)
│   │   └── engine.py             <- NeuroSymbolicRouter orchestrator
│   ├── main.py                   <- FastAPI app with /api/v1/database, /api/v1/placement & /api/v1/ask
│   ├── sql_engine.py             <- Multi-dialect relational query engine connected via db_manager
│   ├── retrieval.py              <- FAISS vector retrieval using FastEmbed (IndexFlatIP)
│   ├── cache.py                  <- Cosine semantic cache for repeat queries
│   ├── grounding.py              <- Grounding verification gate & threshold enforcement
│   ├── llm_engine.py             <- Local in-process GGUF (GPU) & Ollama fallback synthesis
│   └── models.py                 <- Pydantic models for API request/response
├── data/
│   ├── students.db               <- Curated SQLite database (students, staff, courses, skills, openings)
│   ├── documents.json            <- Curated institutional policies, facilities, FAQs
│   ├── faiss.index               <- L2-normalized vector index for cosine similarity
│   └── faiss_meta.json           <- Vector index metadata and document text
├── frontend/                     <- Modern Next.js (Turbopack) Chat & Placement Interface
│   ├── src/components/PlacementMatcherModal.tsx <- Interactive Recruiter & Candidate Suggestion Modal
│   ├── src/components/Header.tsx <- Live DB status indicator & persona switcher
│   └── ...
├── tests/
│   ├── test_database.py          <- Unit tests for db_manager, Supabase/SQLite & health endpoints
│   ├── test_placement.py         <- Unit tests for anti-random matching & skill gap analysis
│   ├── test_router.py            <- Unit tests for Neuro-Symbolic router and context sorter
│   ├── test_sql_engine.py        <- Unit tests for relational queries & profile lookups
│   └── test_api.py               <- End-to-end integration tests for FastAPI endpoints
├── data_setup.py                 <- Seeds SQLite/PostgreSQL tables and builds documents.json
├── run_all.sh                    <- Starts backend (port 9000) and frontend (port 3000)
├── .env                          <- Database credentials (Supabase PostgreSQL connection string)
└── requirements.txt              <- Python dependencies (FastAPI, psycopg2-binary, etc.)
```


---

## Quickstart

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ and npm

### 2. Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Setup SQLite database and curate knowledge documents
python data_setup.py

# Ingest and build FAISS vector index
python -c "from app.ingestion import ingest; ingest()"
```

### 3. Launching the System
Use the unified launcher to start both the FastAPI backend and Next.js frontend:
```bash
chmod +x run_all.sh
./run_all.sh
```

- **Frontend Chat Interface**: `http://localhost:3000`
- **Backend API**: `http://localhost:9000`
- **Interactive Swagger Docs**: `http://localhost:9000/docs`

---

## Testing & Verification

Run the automated test suite verifying all 66 unit and integration tests:
```bash
source venv/bin/activate
python -m unittest discover tests
```

Test coverage includes:
- **`test_database.py`**: Multi-dialect connection, cloud health metrics, parameter translation, dynamic query execution, and API endpoints.
- **`test_placement.py`**: Skill-to-role matching, GPA/attendance cutoffs, skill gap analysis, anti-random candidate ranking, and student role recommendations.
- **`test_router.py`**: Linguistic POS parsing, personal field matching, hybrid intent detection, context priority sorting, and legacy classifier compatibility.
- **`test_sql_engine.py`**: Case-insensitive ID lookups, attendance, CGPA, fee dues, registered courses, faculty mentor, and profile summaries.
- **`test_api.py`**: Health checks, personal SQL queries, missing user ID prompts, vector RAG retrieval, semantic cache hits, hybrid synthesis, and ungrounded refusal gating.


---

## Sample Queries

| Query | Target Engine | Description |
|---|---|---|
| *"What is my attendance?"* | `personal_sql` | Direct relational query over student records (`U101` - `U107`). |
| *"What are my registered courses?"* | `personal_sql` | Queries courses matching student's department and semester. |
| *"What are the central library hours?"* | `vector_rag` | FAISS semantic search over institutional policies. |
| *"Is my attendance high enough for the exams?"* | `hybrid` | Multi-engine offload: student attendance (SQL) evaluated against campus policy (Vector). |
| *"Hello there!"* | `chitchat` | Immediate zero-cost conversational response. |
| *"What is the capital of Mars?"* | `refusal` | Grounding gate prevents hallucination by safely refusing ungrounded topics. |


---

## Architectural Highlights

- **FastEmbed & FAISS IndexFlatIP**: Vectors are strictly L2-normalized so that inner products compute exact cosine similarity without heavy PyTorch runtime overhead.
- **Strict Grounding Quality Gate**: Ensures answers are either accompanied by cited sources with sufficient confidence (`CONFIDENCE_THRESHOLD = 0.28`) or rejected with an honest, polite refusal.
- **Graceful Multi-Engine Degrade**: Works completely in standalone mode without Ollama or external dependencies, with automatic opportunistic upgrade to local SLM/GGUF when available.

