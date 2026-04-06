FROM python:3.11-slim

LABEL org.opencontainers.image.title="InfraMind: Autonomous DevOps Benchmark"
LABEL org.opencontainers.image.description="OpenEnv multi-agent SRE simulation — 5 real-world tasks, seeded reproducibility, adversarial agent"
LABEL org.opencontainers.image.version="5.0.0"

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY env/ ./env/
COPY server.py .
COPY openenv.yaml .

# Copy pre-built UI (built locally before docker build)
# If ui/dist doesn't exist the server falls back to inline HTML
COPY ui/dist/ ./ui/dist/

# Copy inference script (must be at root per hackathon spec)
COPY inference.py .

ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
