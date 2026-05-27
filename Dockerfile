# --- Stage 1: Builder ---
FROM python:3.13-slim AS builder

WORKDIR /app

# adding verbosity for better debugging and ensuring logs are flushed immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN echo "=== INSTALING DEPENDENCIES WITH POETRY ===" \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# --- Stage 2: Final ---
FROM python:3.13-slim AS production
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# 1. Copiar ÚNICAMENTE el entorno virtual compilado y limpio de la etapa anterior
COPY --from=builder /app/.venv /app/.venv

# 2. Copy src code to the final image
COPY src/ /app/src/
COPY src/templates/ /app/templates/
COPY src/static/ /app/static/

# 3 copy Alembic files and folders

COPY alembic.ini /app/
COPY alembic/ /app/alembic/

RUN echo "=== BLUEPRINT ARCHITECTURAL DE HERENCIAPP ===" \
    && ls -R src/

RUN apt-get update && apt-get install -y curl

# 3. Exponer el puerto de la app
EXPOSE 8001

CMD sh -c 'uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload'