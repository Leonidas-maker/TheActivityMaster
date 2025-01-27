# Verwende das Python-Basisimage
ARG PYTHON_VERSION=3.12.8
FROM python:${PYTHON_VERSION}-slim as base

# Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm
ENV DB_HOST=mariadb

WORKDIR /app

# Installiere notwendige Systemabhängigkeiten, inklusive tk
RUN apt-get update && apt-get install -y \
    libtk8.6 \
    tk-dev \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Erstelle einen nicht privilegierten Benutzer
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Installiere Python-Abhängigkeiten
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir -r requirements.txt

# Wechsel zum nicht privilegierten Benutzer
USER appuser

# Kopiere den Quellcode in das Image
COPY . .

# Exponiere den Port
EXPOSE 8001

# Starte die Anwendung
CMD uvicorn 'main:app' --host=0.0.0.0 --port=8001
