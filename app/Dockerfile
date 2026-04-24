FROM python:3.11-slim

WORKDIR /app

# Installation des dependances systeme
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des dependances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source (depuis la racine vers /app car requirements est a la racine)
COPY app/ ./app/
COPY data/ ./data/

# Port d'exposition FastAPI
EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
