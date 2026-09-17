# Dockerfile for FastAPI Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (required for some ML libraries and FAISS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

# Run ingestion script to build FAISS index and metadata
RUN python app/ingestion.py || true

# Run data setup script to build SQLite schemas
RUN python data_setup.py || true

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
