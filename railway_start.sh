#!/usr/bin/env bash
set -e

# Create data directory
mkdir -p /app/data

# Start API in background
uvicorn ect_app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
API_PID=$!

# Wait for API
echo "Waiting for API..."
for i in {1..30}; do
    if curl -s http://localhost:${PORT:-8000}/health > /dev/null 2>&1; then
        echo "API ready."
        break
    fi
    sleep 1
done

# Start Streamlit (on port 8501, proxied by Railway)
streamlit run ect_frontend/app.py \
    --server.port 8501 \
    --server.headless true \
    --server.address 0.0.0.0 \
    --browser.serverAddress 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for either to exit
wait -n $API_PID $STREAMLIT_PID
