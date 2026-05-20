# --- Stage 1: Builder (La cocina de preparación) ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Forzamos a Poetry a crear el entorno virtual exactamente dentro de la carpeta del proyecto
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

# Instalamos Poetry limpiamente en la etapa de compilación
RUN pip install --no-cache-dir poetry

# Copiamos los archivos de manifiesto de dependencias
COPY pyproject.toml poetry.lock ./

# Instalamos únicamente las dependencias de producción (--only main)
# Esto garantiza que pytest/black/mypy se queden fuera de la imagen final para ahorrar espacio en tu EC2
RUN poetry install --only main --no-root --no-interaction --no-ansi

# --- Stage 2: Final (El plato listo para el servidor de Herencia del Abuelo) ---
FROM python:3.13-slim AS production
WORKDIR /app

# Mantener configuraciones de optimización para logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # 🔥 LA MAGIA: Agregamos los binarios del entorno virtual al PATH del sistema operativo del contenedor
    PATH="/app/.venv/bin:$PATH"

# 1. Copiar ÚNICAMENTE el entorno virtual compilado y limpio de la etapa anterior
COPY --from=builder /app/.venv /app/.venv

# 2. Copiar el código fuente indispensable estructurado para producción
COPY src/ /app/src/
COPY templates/ /app/templates/
COPY static/ /app/static/

# 3. Exponer el puerto de la app
EXPOSE 8001

# 4. Punto de entrada (Al estar en el PATH, llamará a uvicorn de forma transparente y global)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]