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
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Set PYTHONPATH so FastAPI can find your src module [cite: 48]
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["gvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]