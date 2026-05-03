# Stage 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
# Generate requirements.txt to avoid installing poetry in final image
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: Final Production Image
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt [cite: 2]
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]