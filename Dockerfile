FROM python:3.11-slim AS base

# ---------------- Basic Environment ----------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------------- System Dependencies ----------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---------------- App Setup ----------------
WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create required folders
RUN mkdir -p games data

# ---------------- Security ----------------
RUN useradd -m appuser
USER appuser

# ---------------- Expose + Healthcheck ----------------
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

# ---------------- Gunicorn Launch ----------------
CMD ["gunicorn", "app:app",
     "--bind", "0.0.0.0:5000",
     "--workers", "3",
     "--threads", "4",
     "--worker-class", "gthread",
     "--timeout", "180",
     "--graceful-timeout", "30",
     "--log-level", "info"]
