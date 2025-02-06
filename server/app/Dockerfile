# Verwende das Python-Basisimage
ARG PYTHON_VERSION=3.12.8
FROM python:${PYTHON_VERSION}-slim as base

# Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm
ENV DB_HOST=mariadb
ENV REDIS_HOST=redis

WORKDIR /app

RUN apt-get update && apt-get install -y curl build-essential

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --no-cache-dir -r requirements.txt

USER appuser

COPY . .

EXPOSE 8001

CMD uvicorn 'main:app' --host=0.0.0.0 --port=8001
