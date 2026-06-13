# HerenciApp

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/poetry-1.8+-orange.svg)](https://python-poetry.org/)

A production-grade web application for restaurant management and control, specifically designed for **Carnitas Herencia del Abuelo**. This project leverages a modern FastAPI backend with a responsive Bootstrap frontend.

## 🛠 Tech Stack

- **Backend:** FastAPI (Python 3.12+).
- **Frontend:** Jinja2 templates with Bootstrap 5.
- **Database:** PostgreSQL (with SQLModel ORM).
- **Auth:** JWT-based authentication with secure password hashing.
- **Infrastructure:** Docker (Multi-stage builds) on AWS EC2.
- **CI/CD:** GitHub Actions.

## 📁 Project Structure

```
herenciapp/
├── src/
│   ├── api/v1/         # Versioned API & App logic
│   │   ├── apps/       # Business modules (Users, Orders)
│   │   └── auth/       # Authentication utilities
│   ├── static/         # CSS and Branding
│   ├── templates/      # Jinja2 HTML templates
│   └── main.py         # Entry point & Lifespan management
├── tests/              # Pytest suite
|    |── integration    # Test with integrated elements (database, endpoints).
|    |── unit           # Test for functions. 
└── docker-compose.yml  # Orchestration for App and DB
```

## 🚀 Getting Started

# Prerequisites
- Python 3.12+
- Poetry
- Docker & Docker Compose

# Local Installation

## Clone and Install:
```
Bash
git clone [https://github.com/ingega/herenciapp.git](https://github.com/ingega/herenciapp.git)
cd herenciapp
poetry install
```
- Environment Setup: Create a .env file with DATABASE_URL, SECRET_KEY, and MAIL_ configurations.

- Run Development Server:
```
Bash
poetry run uvicorn src.main:app --reload
```

## 🧪 Testing & Quality
We follow a Test-Driven mindset:

= Run all tests: poetry run pytest

- Linting: poetry run black src/

- Type Checking: poetry run mypy src/

## 🚢 Production Deployment
The project is deployed to AWS EC2 using Docker and Nginx as a reverse proxy.

Build & Run: docker compose up -d --build

CI/CD: Pushing to main triggers automated testing and deployment via GitHub Actions.

## 📄 License
Proprietary for Herencia del Abuelo.