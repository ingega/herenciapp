# src/database.py

from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker
from .config import settings

# 1. Database URL selection (Production vs. Mock/Sandbox)
# This allows us to switch environments just by changing the .env file

DATABASE_URL = settings.DATABASE_URL

print(f"[DEBUG DB] Cargando URL del motor: "
      f"{DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}", flush=True)

# 2. Create the Engine
# 'echo=False' for production to keep logs clean; 'echo=True' for debugging
### debugging: adding flush=True to ensure logs are printed immediately in Docker
print("[DEBUG DB] Instanciando create_engine...", flush=True)
engine = create_engine(
    DATABASE_URL, 
    echo=settings.DEBUG,
    future=True,
    pool_size=5,          # Máximo de conexiones persistentes abiertas simultáneamente
    max_overflow=10,      # Conexiones adicionales permitidas en picos altos de tráfico
    pool_timeout=30,      # Segundos de espera antes de lanzar un timeout si el pool está lleno
    pool_recycle=1800     # Recicla las conexiones cada 30 minutos para evitar hilos zombis
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

    ### debugging: adding flush=True to ensure logs are printed immediately in Docker
    print("[DEBUG DB] Generando sesión de base de datos...", flush=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        ### debugging: adding flush=True to ensure logs are printed immediately in Docker
        print("[DEBUG DB] Cerrando sesión de base de datos...", flush=True)
        db.close()

# 5. Database Initialization
def init_db():
    """
    Creates the tables defined in our models. 
    In production, we'll eventually transition this to Alembic migrations.
    """
    print("[DEBUG DB] Iniciando la función init_db(). Creando tablas de SQLModel...", flush=True)
    try:
        SQLModel.metadata.create_all(engine)
        print("[DEBUG DB] SQLModel.metadata.create_all completado exitosamente sin errores.", flush=True)
    except Exception as e:
        print(f"[CRITICAL DB] Error devastador al mapear tablas: {type(e).__name__} -> {str(e)}", flush=True)
        raise e

# get a session for direct use in services (not recommended for routes)
def get_session() -> Session:
    """
    Provides a new database session. 
    This is for internal use in services, not for FastAPI routes.
    """
    return SessionLocal()