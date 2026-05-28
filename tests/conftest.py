from datetime import timedelta

import pytest, logging
from typing import Generator
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from src.api.v1.apps.users.models import User
from src.api.v1.auth.auth import create_access_token

from src.main import app
from src.database import get_db, get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# debug routes
for route in app.routes:
    logger.info(f'valid route: {route.path}')

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
        return session

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
    token_data = {"sub": test_user.email}
    
    # 2. Build the token string using your existing utility helper
    # (assuming it accepts data and an optional expiration window)
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=15))
    
    # 3. Return the exact cookie key-value configuration.
    # Replace 'access_token' with your app's actual cookie name (e.g., settings.COOKIE_NAME)
    return {"access_token": token}