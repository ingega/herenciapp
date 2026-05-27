import pytest, logging
from typing import Generator
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

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