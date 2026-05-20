# --- Stage 1: Builder ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Desactivar la creación de entornos virtuales interactivos para acelerar el pipeline
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry && poetry self add poetry-plugin-export
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# --- Stage 2: Final ---
FROM python:3.13-slim AS production
WORKDIR /app

# Evitar que Python escriba archivos .pyc en disco y asegurar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 1. Copiar el archivo generado
COPY --from=builder /app/requirements.txt .

# 2. Instalar dependencias limpiamente
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar únicamente el código fuente indispensable (Evita basura local si no tienes .dockerignore)
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/

# 4. Exponer el puerto de la cocina
EXPOSE 8001

# 5. Punto de entrada limpio (Llamando directamente a uvicorn global de pip)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]