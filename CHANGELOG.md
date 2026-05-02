# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and configuration
- Basic project structure with `src/` and `tests/` directories
- Poetry dependency management
- FastAPI framework integration
- Uvicorn development server configuration
- Dockerfile for containerizing the application
- GitHub Actions workflow for automated deployment to EC2

### Changed
- Updated project description for clarity

### Fixed
- N/A

## [0.1.2] - 2026-05-02

### Added
- Environment settings support with `pydantic-settings` and `.env` support
- New `src/config.py` module for restaurant metadata and app configuration
- Test coverage for the root route using FastAPI `TestClient`

### Changed
- Added `pytest` and `httpx` to dev dependencies
- Updated `pyproject.toml` and `poetry.lock` for new dependencies

### Fixed
- N/A

## [0.1.1] - 2026-05-01

### Added
- Basic FastAPI application with Jinja2 templating support
- HTML template (index.html) with Bootstrap 5 styling
- Static files structure for CSS and other assets
- Enhanced dependencies: `uvicorn[standard]` and `jinja2`
- Poetry lock file generated

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

## [0.1.0] - 2026-04-30

### Added
- Project initialized with Poetry
- FastAPI dependency added
- Uvicorn added to development dependencies
- Basic README and CHANGELOG files created
- Project structure established