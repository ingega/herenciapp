# HerenciApp

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/poetry-1.8+-orange.svg)](https://python-poetry.org/)

A production-grade web application for restaurant management and control, specifically designed for **Herencia del Abuelo**. This project leverages a modern Python backend with a traditional, responsive frontend.

## 🛠 Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+).
- **Frontend:** [Jinja2](https://jinja.palletsprojects.com/) templates for server-side rendering.
- **Styling:** [Bootstrap 5](https://getbootstrap.com/) for a mobile-first responsive UI.
- **Dependency Management:** [Poetry](https://python-poetry.org/).
- **Infrastructure:** [Docker](https://www.docker.com/) (Multi-stage builds) and AWS EC2.
- **CI/CD:** GitHub Actions.

## 📁 Project Structure

```text
herenciapp/
├── src/                # Source code
│   ├── main.py         # App entry point & FastAPI initialization
│   ├── routes/         # API and Web route definitions
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS, JS, and Images (Bootstrap & Logos)
├── tests/              # Pytest suite
├── .github/workflows/  # CI/CD (deploy.yml)
├── Dockerfile          # Multi-stage production build
├── pyproject.toml      # Poetry dependencies
└── .env.example        # Template for environment variables
```

## **🚀 Getting Started**
# Prerequisites
- Python 3.12 or higher
- Poetry installed (curl -sSL https://install.python-poetry.org | python3 -)

# Local Installation
Clone the repository:
```
Bash
git clone [https://github.com/ingega/herenciapp.git](https://github.com/ingega/herenciapp.git)
cd herenciapp
```
# Install dependencies:
```
Bash
poetry install
```
# Set up environment variables:
```
Create a .env file in the root directory and add your configurations (e.g., APP_ENV=development).
```
# Running the Development Server
```
Bash
poetry run uvicorn src.main:app --reload
```
**The application will be available at http://localhost:8000**

## **🧪 Testing & Quality**
We maintain a "Test-Driven" mindset for production readiness.

**Run Tests:** poetry run pytest

**Linting:** poetry run black src/

**Type Checking:** poetry run mypy src/

## 🚢 Production Deployment
Docker
The project uses a multi-stage Dockerfile to ensure the production image is slim and secure, excluding development tools like Poetry from the final build.
```
Bash
docker build -t herenciapp .
docker run -d -p 8000:8000 --name herenciapp-container herenciapp
CI/CD Workflow
```
Pushing to the main branch triggers the deploy.yml workflow:

*Build & Test:* Runs the full suite of Pytests to ensure stability.

*Deploy:* Automatically connects to the AWS EC2 instance via SSH, pulls the latest code, and restarts the Docker container.

## 📄 **License**
This project is proprietary and developed for Herencia del Abuelo.