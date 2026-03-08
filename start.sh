#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  Entity Compliance Tracker"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/.installed" ]; then
    echo "Installing dependencies (first run only)..."
    pip install -q --upgrade pip
    pip install -q .
    touch .venv/.installed
    echo "Dependencies installed."
fi

# Create data directory
mkdir -p data

echo ""
echo "Starting services..."
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:8501"
echo ""
echo "Press Ctrl+C or use the Shutdown button in the UI to stop."
echo ""

# Cleanup: kill all child processes
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $API_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    wait $STREAMLIT_PID 2>/dev/null || true
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start API in background
uvicorn ect_app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "API is ready."
        break
    fi
    sleep 1
done

# Start Streamlit
streamlit run ect_frontend/app.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!

# Open browser (macOS)
sleep 2
if command -v open &> /dev/null; then
    open http://localhost:8501
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501
fi

# Wait for either process to exit
wait -n $API_PID $STREAMLIT_PID 2>/dev/null || true
cleanup
