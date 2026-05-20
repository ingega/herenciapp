# --- Stage 1: Builder (La cocina de preparación) ---
FROM python:3.13-slim AS builder

WORKDIR /app

# adding verbosity for better debugging and ensuring logs are flushed immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] INICIANDO ETAPA BUILDER ===" >> installation-debug.txt

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

# Instalamos Poetry limpiamente en la etapa de compilación
RUN pip install --no-cache-dir poetry

# Copiamos los archivos de manifiesto de dependencias
COPY pyproject.toml poetry.lock ./

RUN echo "=== INSTALING DEPENDENCIES WITH POETRY ===" \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# --- Stage 2: Final (El plato listo para el servidor de Herencia del Abuelo) ---
FROM python:3.13-slim AS production
WORKDIR /app

# Mantener configuraciones de optimización para logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # LA MAGIA: Agregamos los binarios del entorno virtual al PATH 
    # del sistema operativo del contenedor
    PATH="/app/.venv/bin:$PATH"

RUN echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] INICIANDO ETAPA DE EJECUCIÓN ===" >> installation-debug.txt

# 1. Copiar ÚNICAMENTE el entorno virtual compilado y limpio de la etapa anterior
COPY --from=builder /app/.venv /app/.venv

# 2. Copiar el código fuente indispensable estructurado para producción
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/

RUN echo "=== BLUEPRINT ARCHITECTURAL DE HERENCIAPP ===" \
    && ls -R src/ \
    && echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] ARCHITECT BLUEPRINT ===" >> installation-debug.txt

RUN apt-get update && apt-get install -y curl

# 3. Exponer el puerto de la app
EXPOSE 8001

RUN echo """=== STARTING UVICORN ===""" \
&& echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] STARTING UVICORN ===" >> installation-debug.txt

# 4. Punto de entrada (Al estar en el PATH, llamará a uvicorn de forma transparente y global)
CMD sh -c '\
echo "=== CONTAINER STARTED $(date) ===" >> /app/installation-debug.txt && \
echo "=== TESTING PYTHON ===" >> /app/installation-debug.txt && \
python --version >> /app/installation-debug.txt 2>&1 && \
echo "=== TESTING UVICORN ===" >> /app/installation-debug.txt && \
which uvicorn >> /app/installation-debug.txt 2>&1 && \
echo "=== STARTING APP ===" >> /app/installation-debug.txt && \
uvicorn src.main:app --host 0.0.0.0 --port 8001 \
>> /app/installation-debug.txt 2>&1'