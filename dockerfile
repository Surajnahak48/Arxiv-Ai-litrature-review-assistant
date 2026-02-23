FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend ./backend
COPY frontend ./frontend
COPY data ./data

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Start both backend + frontend
CMD uvicorn backend.api:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0