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

## [1.9.4] 2026-06-01
This version is for address the addition of new meat catalogue function

### Added
- Meat catalogue schemas in `src/api/v1/apps/orders/schemas.py`

### Changed
- N/A

### Fixed
- N/A

## [1.9.3] 2026-06-01

### Added
- N/A

### Changed
- constraint in flavor catalogue in `src/api/v1/apps/orders/models.py` the change was made in commit `7642dc365f09e59db5207771ff41cb26f2797286`

### Fixed
- Alembic sequence to fix the pipeline, the change was made in commit `7642dc365f09e59db5207771ff41cb26f2797286`

## [1.9.2]

### Added
- Model for meat catalogue

### Changed
- Ran database migrations with alembic

### Fixed
- Alembic migrations to add the new table

## [1.9.1]

### Added
- N/A

### Changed
- N/A

### Fixed
- Edited labels in `src/templates/flavors/list
- Added current user to the context for ui endpoints in `src/api/v1/apps/orders/routes.py`

## [1.9.0] 2026-05-31
This version added the templates for flavors handling

### Added
- template for flavors handling in `src/templates/flavors/list.html`
- endpoint for ui in `src/api/v1/apps/orders/routes.py`
- template for flavors adding record in `src/templates/flavors/create.html`
- added all the logic for update and delete flavors in `src/templates/flavors/list.html`
- added test suite for flavors templates in `tests/integration/test_flavors_template.py`

### Changed
- Added flavors option to main nav bar in `src/templates/base_nav.html`

### Fixed
- N/A

## [1.8.1] 2026-05-31

### Added
- N/A

### Changed
- N/A

### Fixed
- removing items from list in `tests/integration/test_endpoint_main_and_orders.py`

## [1.8.0] 2026-05-31
This version add the flavors endpoints, templates and tests

### Added
- endpoint get_flavor_by_id in `src/api/v1/apps/orders/router.py`
- schemas for flavors in `src/api/v1/apps/orders/schemas.py`
- endpoints for flavors in `src/api/v1/apps/orders/router.py`
- test for post and get endpoints in `test/integration/test_flavor_post_get_endpoint.py`
- test for patch and delete endpoints in `test/integration/test_flavor_patch_delete_endpoint.py`


### Changed
- Added protected routes in `tests/integration/test_endpoint_main_and_orders.py`

### Fixed
- N/A

## [1.7.3]

### Added
- N/A

### Changed
- Refactored main.html adding style and elements

### Fixed
- N/A

## [1.7.2] 2026-05-28
Added endpoints for updata and delete products
Added logs in documentation
Bumped version

### Added
- Update product Schema in `src/api/v1/orders/schemas.py`
- enpoints for update/delete in `src/api/v1/orders/router.py`
- test for update/delete products endpoints in `test/integration/test_update_and_delete_products_enpoints.py`
- endpoint to retrieve product by id in `src/api/v1/apss/orders/routes.py`
- template for update/delete product in `src/templates`
- test for enppoint orders/products/{id} in `tests/integration/test_products.py`
- test for template products/updte in `tests/integration/test_update_products.py`

### Changed
- Added a edit button for products/update endpoint in `src/templates/product_update.html`

### Fixed
- Added response status code 200 to patch product endpoint in `src.api.v1.apps.orders.router.py`

## [1.7.1]

### Added
- products test suite in `tests/integration/test_products.py`
- `base_nav.html` template in `src/templates`
- `products.html` template in `src/templates`
- test for product template in `tests/integration/test_products_template.py`

### Changed
- Added a mock app for test suite in `tests/conftest.py`
- Added a get_session for mock tests in `tests/conftest.py`

### Fixed
- Added mocked access token for auth validation in tests in `src/tests/conftest.py`

## [1.7.0]
Branch name: products-endpoint
This tag creates the endpoint for adding products, and the tests for the endpoint
The bumping version is due to a new addition to save data.

### Added
- `services.py` in `src/api/v1/apss/orders/`
- Class `Products`in `src/api/v1/apss/orders/services.py`
- endpoint POST orders/products in `src/api/v1/apss/orders/routes.py`

### Changed
- N/A

### Fixed
- N/A

## [1.6.7] 2026-05-26
- branch name: add-orders-schemas
  This version add the neccessary schemas for orders models.

### Added
- file `src/api/v1/apps/orders/schemas.py`
- Schemas for orders in `src/api/v1/apps/orders/schemas.py`
- `orders` image in `src/static/images`

### Changed
- N/A

### Fixed
- N/A

## [1.6.6] 2026-05-26
This version add the orders tables and schemas.

### Added
- models in `src/api/v1/apps/orders/models.py`
- models imporation in `alembic/env.py`

### Changed
- Adding sqlmodel importation to alembic script in `alembic/script.py.mako`

### Fixed
- Using smallintenger function from sqlalchemy in `src/api/v1/apps/orders/models.py` 

## [1.6.5] 2026-05-25
Installation and configuration of alembic

### Added
- `alembic.ini` file and `alembic` directory

### Changed
- Changing connection for use of env in `alembic/env.py`

### Fixed
- N/A

## [1.6.4]

### Added
- N/A

### Changed
- N/A

### Fixed
- Changing endpoint orders/orders for orders/ in `src/api/v1/apps/orders/route.py`

## [1.6.3] 2026-05-25
- testing for endpoints and functions in validation flow

### Added
- Unit test in `tests/unit/test_creation_and_validation_token.py`
- Added MagicMock class to avoid send email licking in `tests/unit/test_creation_and_validation_token.py`
- integration test for actual protected endpoint (main and orders/orders) in `test/integration/test_endpoint_main_and_orders.py`

### Changed
- N/A

### Fixed
- Updating select statement instead query in `src/app/v1/auth/services.py`
- Adding mock_send to avoid licking sending real emails in `tests/unit/test_creation_and_validation_token.py` and `tests/integration/test_user_verification.py` 

## [1.6.2]

### Added
- Template for orders in `src/templates`

### Changed
- N/A

### Fixed
- enpoint logic for orders enpoint in `src/app/v1/apps/orders/router.py`

## [1.6.1]

### Added 2026-05-24
- Added placeholder orders template in `src/templates/orders.html`
- `router.py` in `src/app/v1/orders/`
- orders endpoint in `src/app/v1/orders/router.py`

### Changed
- N/A

### Fixed
- N/A

## [1.6.0]

### Added
- auth flow in `src/app/v2/auth/auth.py`
- function get_current_user_from_cookie in `src/api/v1/auth/auth.py`
- Added template for orders panel

### Changed
- added env variables in `.env` file
- bumping version in `src/__init__.py` file

### Fixed
- Enhanced error handling for 401 in `src/main.py`

## [1.5.1] 2026-05-23

### Added
- placeholder for main logic `src/templates/main.html`

### Changed
- Adding logic to reach main

### Fixed
- N/A

## [1.5.0] 2026-05-23

### Added
- register template in `src/templates/register.html`

### Changed
- removing the txt debug deploying files

### Fixed
- relative static path in `src/main.py`

## [1.4.9]

### Added
- Debugging prints in Dockerfile, and database.py, main.py and confing.py in `src/app/v1/apps`

### Changed
- N/A

### Fixed
- N/A

## [1.4.8]

### Added
- N/A

### Changed
- Refactored Dockerfile and yml files for deploying in EC2

### Fixed
- Test for verification endpoint

## [1.4.7]

### Added
- N/A

### Changed
- refactored main users route in `src/main.py`
- refactored tests in `test/integration/test_user_verification.py`
- Bumping version in `__init__.py` file

### Fixed
- N/A

## [1.4.6] - 2026-05-15

### Added
- N/A

### Changed
- Bumping version in `__init__.py` file

### Fixed
- adding builder for test in `docker-compose.yml`

## [1.4.5] - 2026-05-15

### Added
- test for user verification in `test/integration/test_user_verification.py`

### Changed
- Bumpoing version in `__init__.py` file

### Fixed
- N/A

## [1.4.4]

### Added
- N/A

### Changed
- Bumped version in `__initi__.py`

### Fixed
- Async function in `test/unit/test_auth_services.py`

## [1.4.3] 2026-05-15

### Added
- N/A

### Changed
- N/A

### Fixed
- Refactored importations for auth tests in `test/unit/test_auth_services.py`

## [1.4.2] 2026-05-15

### Added
- N/A

### Changed
- N/A

### Fixed
- Async for verify existin user in function `create_user` in `src/app/v1/apps/users/services.py`
- Added async logic for functions in `test/unit/test_auth_services`

## [1.4.1] - 2026-05-14

### Added
- N/A

### Changed
- added config dict in the VerificationToken schema in `src/api/v1/apps/users/schemas.py`

### Fixed
- async mode for create_user function in `src/api/v1/apps/users/services.py`

## [1.4.0] - 2026-05-14

### Added
- Added `src/api/v1/auth/services.py` to support verification token creation and email verification.
- Added `VerificationToken` SQLModel in `src/api/v1/apps/users/models.py` for persistent token storage.
- Added `UserVerificationSchema` and `TokenCreate` schemas in `src/api/v1/apps/users/schemas.py`.
- Added email verification endpoints and enhanced logging in `src/api/v1/apps/users/router.py`.

### Changed
- Updated package version in `src/__init__.py` to `1.4.0`.
- Updated `src/api/v1/apps/users/services.py` to use async verification flow, token generation, and stronger user retrieval handling.
- Updated verification error details and duplicate-email messaging in `src/api/v1/apps/users/router.py`.

### Fixed
- Improved verification token persistence and email failure logging in `src/api/v1/apps/users/services.py`.

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