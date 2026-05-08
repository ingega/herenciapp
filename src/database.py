# src/database.py

from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker
from .config import settings

# 1. Database URL selection (Production vs. Mock/Sandbox)
# This allows us to switch environments just by changing the .env file

DATABASE_URL = settings.DATABASE_URL

# 2. Create the Engine
# 'echo=False' for production to keep logs clean; 'echo=True' for debugging
engine = create_engine(
    DATABASE_URL, 
    echo=settings.DEBUG,
    future=True
)

# 3. Session Factory
# We use sessionmaker to ensure we can create fresh, isolated sessions for every request
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=Session
)

# 4. The "Dependency Injection" Sauce
# This is how we provide a database session to our FastAPI routes safely 
def get_db():
    """
    Generator function to provide a DB session.
    It automatically closes the session after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Database Initialization
def init_db():
    """
    Creates the tables defined in our models. 
    In production, we'll eventually transition this to Alembic migrations.
    """
    SQLModel.metadata.create_all(engine)

# get a session for direct use in services (not recommended for routes)
def get_session() -> Session:
    """
    Provides a new database session. 
    This is for internal use in services, not for FastAPI routes.
    """
    return SessionLocal()