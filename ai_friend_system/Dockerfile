FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---------- System dependencies ----------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    git \
    curl \
    ffmpeg \
    portaudio19-dev \
    redis-tools \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade ollama

# ---------- App code ----------
COPY . /app

# ---------- Entrypoint script (ensure executable) ----------
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

# ---------- Use entrypoint for migrations ----------
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# ---------- Default command (API) ----------
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
