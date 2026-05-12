# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- N/A

### Fixed
- N/A

## [1.3.4] - 2026-05-12

### Added
- Added `UserOut` schema in `src/api/v1/apps/users/schemas.py` for serialized user responses.
- Included `users_router` from `src/api/v1/apps/users/router.py` in `src/main.py` to expose user management route handling.
- Added new package files for user app routing in `src/api/v1/apps/users/__init__.py` and `src/api/v1/apps/users/router.py`.

### Changed
- Updated `README.md` content, formatting, and project branding to **Carnitas Herencia del Abuelo**.
- Extended email configuration settings in `src/config.py` with `MAIL_STARTTLS`, `MAIL_SSL_TLS`, `USE_CREDENTIALS`, and `VALIDATE_CERTS`.

### Fixed
- N/A

## [1.3.3] - 2026-05-11

### Added
- a verification tests in `tests/unit/test_verification.py` using a mock send email function.

### Changed
- Added dummy variables for tests execution in `.github/workflows/deploy.yml`
- version label in `src/__init__.py`

### Fixed
- N/A

## [1.3.2] - 2026-05-08

### Added
- Verification fields `verification_code` and `code_expires_at` to `src/api/v1/apps/users/models.py`
- `src/api/v1/apps/users/email_service.py` for sending verification emails
- `create_pending_user()` service in `src/api/v1/apps/users/services.py` for inactive user registration and verification code generation
- `generate_verification_token()` helper in `src/api/v1/auth/utils.py`
- Added fastapi-mail for mail sending.

### Changed
- Added `UserCreate` schema validation messages in `src/api/v1/apps/users/schemas.py` with Spanish password requirement text
- Updated `src/__init__.py` version metadata to `1.3.2`
- `src/api/v1/auth/utils.py` now includes secure token generation for email confirmation

### Fixed
- Improved service creation flow with race-condition handling and rollback safety in `src/api/v1/apps/users/services.py`

## [1.3.1]

### Added
- `get_user_by_id`, `get_all_users`, and `delete_user` service functions in `src/api/v1/apps/users/services.py`
- New service test coverage for CRUD behavior and edge cases in `tests/unit/test_auth_services.py`

### Changed
- `update_user` in `src/api/v1/apps/users/services.py` now supports `is_active` updates and refreshes `last_modification`
- Service tests reorganized with additional validation and behavior checks for user lifecycle operations

### Fixed
- Improved service error handling, rollback safety, and logging in `src/api/v1/apps/users/services.py`

## [1.2.8]

### Added
- functions session_fixture and client_fixture for database connection testing in `test/conftest.py`

### Changed

### Fixed

## [1.2.6] - 2026-05-07

### Added
- services in `src/api/users/services.py`

### Changed
- N/A

### Fixed
- N/A

## [1.2.5] - 2026-05-07

### Added
- verify_password function in `src/api/auth/utils.py`

### Changed
- N/A

### Fixed
- N/A

## [1.2.4] - 2026-05-07

### Added
- Authentication utilities in `src/api/auth/utils.py`
- `get_session()` function in `src/database.py` for service layer database access

### Changed
- Enhanced user services in `src/api/v1/users/services.py` with logging, error handling, and data normalization
- Moved password hashing utilities from `src/api/v1/users/utils.py` to `src/api/auth/utils.py`

### Removed
- `src/api/v1/users/__init__.py`
- `src/api/v1/users/utils.py`

## [1.2.3] - 2026-05-07

### Added
- function get_user_by_id in `src/api/v1/users/services.py`

### Changed
- N/A

### Fixed
- N/A

## [1.2.2] - 2026-05-07

### Added
- function get_user_by_email in `src/api/v1/users/services.py`

### Changed
- N/A

### Fixed
- N/A

## [1.2.1] - 2026-05-07

### Added
- User API structure with models, services, and utilities in `src/api/v1/users/`
- User model moved to `src/api/v1/users/models.py`
- User creation service in `src/api/v1/users/services.py`
- Password hashing utility in `src/api/v1/users/utils.py`

### Changed
- Moved authentication models from `src/models/auth.py` to `src/api/v1/users/models.py`

### Removed
- `src/models/` directory and its contents

## [1.1.1] - 2026-05-05

### Added
- Database authentication dependencies: bcrypt, sqlalchemy, alembic, sqlmodel, psycopg2
- Initial models structure: src/models/auth.py
- Settings loader with cached `get_settings()` factory for application configuration

### Changed
- Updated poetry.lock with new packages
- Poetry version updated to 2.4.0
- `src/main.py` now initializes FastAPI with `get_settings()` and imports `StaticFiles`
- Added production/mock database configuration support and dynamic `DATABASE_URL` construction in `src/config.py`

### Fixed

## [1.1.0] - 2026-05-05

### Added
- database connection in `docker-compose.yml` file

### Changed

### Fixed

## [1.0.1] - 2026-05-05

### Added
- health endpoint
- test for health endpoint
- folder structure for applications

### Changed
- Adding cleanup commands for EC2 instance in `deploy.yml` file

### Fixed

## [1.0.0] - 2026-05-04
### Added
- Initial production-grade MVP for Herencia del Abuelo.
- FastAPI backend with Jinja2 frontend integration.
- Mobile-first responsive UI using Bootstrap.
- Multi-stage Dockerfile for slim production images.
- Automated CI/CD pipeline via GitHub Actions to AWS EC2.
- Professional README.md and project documentation.

## [0.1.9] - 2026-05-04

### Changed
- Dockerfile refactor for install requirements in EC2
- __version__ update

## [0.1.8] - 2026-05-04

### Added
- version metadata
- installated of poetry-export plugin to use with poetry >= 2.4

### Changed
- Updated `Dockerfile` and `docker-compose` files port from 8000 to 8001

### Fixed
- `Dockerfile` structure, separating COPY from RUN line. and removing a wrong comment


## [0.1.7] - 2026-05-02

### Added
- removed security files in `.gitignore`

### Changed
- Updated project.toml for use as project, instead a package
- Updated Python base image to use 3.13
- Refactored `deploy.yml` file to save space in EC2 instance
- Added `python -m` commands to `Dockerfile`

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