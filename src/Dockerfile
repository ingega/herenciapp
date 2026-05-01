FROM python:3.11-slim

# System dependencies for Poetry and Python
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (no dev tools for production-grade)
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy the source code (assuming your app is in /src)
COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]