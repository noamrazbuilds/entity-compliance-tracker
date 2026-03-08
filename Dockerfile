FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY ect_app/ ect_app/
COPY ect_frontend/ ect_frontend/
COPY data/ data/

# Install dependencies
RUN pip install --no-cache-dir .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "ect_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
