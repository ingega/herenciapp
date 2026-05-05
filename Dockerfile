# --- Stage 1: Builder ---
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install poetry && poetry self add poetry-plugin-export
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# --- Stage 2: Final ---
FROM python:3.13-slim
WORKDIR /app

# 1. Copy the requirements file from the builder
COPY --from=builder /app/requirements.txt .

# 2. INSTALL the requirements in this final stage

RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your source code
COPY . .

# 4. Set the environment so Python finds your 'src' folder
ENV PYTHONPATH=/app

# 5. Start the server as a module
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]