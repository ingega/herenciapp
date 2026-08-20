from datetime import timedelta

import pytest, logging
from typing import Generator
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from src.api.v1.apps.users.models import User
from src.api.v1.auth.auth import create_access_token

import os
# Ensure env vars for mail so ConnectionConfig validation does not fail during imports
os.environ.setdefault('MAIL_USERNAME', 'test')
os.environ.setdefault('MAIL_PASSWORD', 'test')
os.environ.setdefault('MAIL_FROM', 'test@local')

# Patch the mail client factory to avoid ConnectionConfig validation during tests.
# This ensures send_verification_email can be called and the test-level patch of
# FastMail.send_message will correctly intercept or we provide a harmless default.
from src.api.v1.apps.users import email_service as _email_service

class _DummyMailClient:
    async def send_message(self, message):
        return True

# Replace the factory with one that returns a dummy client when env is not configured
try:
    _email_service.get_mail_client = lambda: _DummyMailClient()
except Exception:
    pass

from src.main import app
from src.database import get_db, get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure mail config is available during tests so ConnectionConfig validation succeeds
import pytest as _pytest

@_pytest.fixture(scope="session", autouse=True)
def _ensure_mail_settings():
    try:
        import src.config as _config
        _config.settings.MAIL_USERNAME = _config.settings.MAIL_USERNAME or "test"
        _config.settings.MAIL_PASSWORD = _config.settings.MAIL_PASSWORD or "test"
        _config.settings.MAIL_FROM = _config.settings.MAIL_FROM or "test@local"
    except Exception:
        pass
    yield

# debug routes (safely attempt to log route path or prefix)
for route in app.routes:
    try:
        route_id = getattr(route, 'path', None) or getattr(route, 'prefix', None) or repr(route)
    except Exception:
        route_id = repr(route)
    logger.info(f'valid route: {route_id}')

# 1. Setup an in-memory SQLite database for testing
sqlite_url = "sqlite://"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Creates a clean database session for each test.
    It creates all tables before the test and drops them after.
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Overrides the get_db dependency in our FastAPI app to use the 
    testing session instead of the real production database.
    """
    def get_session_override():
        # Provide a fresh session for each request (avoids long-lived identity-map issues)
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="app")
def app_fixture():
    return app

# validate user credentials for authenticated tests
@pytest.fixture(scope="function")
def test_user(session):
    """
    Creates a temporary mock user inside the test database session.
    """
    user = User(
        email="partner@herenciapp.com",
        hashed_password="fakehashedpassword123!",
        is_active=True,
        is_verified=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(scope="function")
def authorized_client_cookies(test_user):
    """
    Generates a valid signed access token cookie dictionary for the TestClient.
    """
    # 1. Create token data structure matching what your auth middleware expects
    token_data = {"sub": test_user.email, "user_id": test_user.id, "role": "admin"}
    
    # 2. Build the token string using your existing utility helper
    # (assuming it accepts data and an optional expiration window)
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=15))
    
    # 3. Return the exact cookie key-value configuration.
    # Replace 'access_token' with your app's actual cookie name (e.g., settings.COOKIE_NAME)
    return {"access_token": token}