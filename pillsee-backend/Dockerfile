# PillSee Backend Dockerfile
FROM python:3.9-slim

# Nastavení working directory
WORKDIR /app

# Instalace system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements a instalace Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy aplikační kód
COPY app/ ./app/
COPY main.py ./

# Vytvoření non-root uživatele
RUN groupadd -r pillsee && useradd -r -g pillsee pillsee
RUN chown -R pillsee:pillsee /app
USER pillsee

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Spuštění aplikace
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]