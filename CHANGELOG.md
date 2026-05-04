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

## [0.1.8] - 2026-05-04

### Added
- version metadata

### Changed
- Updated `Dockerfile` and `docker-compose` files port from 8000 to 8001

### Fixed
- `Dockerfile` structure, separating COPY from RUN line.


## [0.1.7] - 2026-05-02

### Added
- removed security files in `.gitignore`

### Changed
- Updated project.toml for use as project, instead a package
- Updated Python base image to use 3.13
- Refactored `deploy.yml` file to save space in EC2 instance

### Fixed
- Moved *package-mode* var in `pyproject.toml` file to tool.poetry section

## [0.1.6] - 2026-05-02

### Added
- Automated test execution step in GitHub Actions workflow to validate code before deployment

### Changed
- Simplified Dockerfile to use `poetry export` for generating `requirements.txt` instead of installing poetry in the final image
- Updated Python base image to version 3.12 in both builder and final stages
- Refactored GitHub Actions workflow to use `docker-compose up` for streamlined container orchestration
- Updated EC2 deployment paths and automation script (`cd ~/herenciapp`)
- Renamed workflow to "Deploy Herenciapp to EC2" for clarity

### Fixed
- N/A

## [0.1.5] - 2026-05-02

### Added
- Production-ready Docker multi-stage build with a separate builder stage for dependency installation
- Non-root runtime configuration and Uvicorn set to run with 4 workers for improved performance

### Changed
- Updated `README.md` with Python 3.12 / Poetry 1.8 requirements, clearer project description, and enhanced onboarding instructions
- Refined the main template layout in `src/templates/index.html` with improved card styling, logo presentation, and localized restaurant metadata display

### Fixed
- N/A

## [0.1.4] - 2026-05-02

### Added
- Expanded root endpoint tests in `tests/test_main.py` with full response validation and logo rendering checks
- Added a dedicated test for static file serving configuration and image path generation

### Changed
- Removed `.gitignore` exclusion for `src/static/images/` to allow media file tracking
- Refined home page validation logic and test coverage for restaurant config values

### Fixed
- N/A

## [0.1.3] - 2026-05-02

### Added
- Restaurant logo configuration with `RESTAURANT_LOGO_NAME` and `SHOW_LOGO` settings in `config.py`
- Optional logo display in the main template with conditional rendering
- Spanish language updates to the index page for restaurant details
- Media files ignore pattern in `.gitignore` for `src/static/images/*`

### Changed
- Updated app title to use dynamic `APP_NAME` from settings
- Enhanced template context with global config access
- Localized UI text to Spanish for restaurant information display

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