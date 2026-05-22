FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 1. Ingest dependencies manifests
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy all backend elements (src/, vector_db/, etc.) directly into /app
COPY . .

EXPOSE 8000

# 3. Fire up Uvicorn directly targeting src.main:app because /app is the root!
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]