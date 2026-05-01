# HerenciApp

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/poetry-2.0+-orange.svg)](https://python-poetry.org/)

A modern web application for restaurant management and control, built with FastAPI. Originally designed for "Carnitas Herencia del Abuelo" restaurant.

## Features

- **FastAPI Framework**: High-performance, easy-to-use web framework
- **Restaurant Management**: Comprehensive tools for restaurant operations
- **Modern Python**: Built with Python 3.13+ and Poetry for dependency management
- **API-First Design**: RESTful API endpoints for seamless integration

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ingega/herenciapp.git
   cd herenciapp
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

### Development Server

Run the development server with Uvicorn:

```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## Project Structure

```
herenciapp/
├── src/                 # Source code
├── tests/              # Test files
├── pyproject.toml      # Poetry configuration
├── README.md           # This file
├── CHANGELOG.md        # Version history
└── .env               # Environment variables
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black src/
poetry run isort src/
```

### Type Checking

```bash
poetry run mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Edmundo Garcia - [70769598+ingega@users.noreply.github.com](mailto:70769598+ingega@users.noreply.github.com)

Project Link: [https://github.com/ingega/herenciapp](https://github.com/ingega/herenciapp) 
