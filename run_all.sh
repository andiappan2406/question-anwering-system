#!/bin/bash
echo "Starting Backend on Port 9000..."
source venv/bin/activate
uvicorn app.main:app --port 9000 --reload &
BACKEND_PID=$!

echo "Starting Frontend on Port 3001..."
cd frontend
npm run dev -- -p 3001 &
FRONTEND_PID=$!

# Wait for both background processes to finish
wait $BACKEND_PID $FRONTEND_PID
