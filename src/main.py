import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from src.config import settings
from src.router import api_router
from src.__init__ import __version__ as version
from .database import init_db
from .api.v1.apps.users.router import router as users_router

# Configuración del logger oficial de producción para el EC2
logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Administrador del ciclo de vida de la aplicación.
    Maneja el arranque seguro de la base de datos sin congelar el Event Loop.
    """
    logger.info("Fuego encendido: Iniciando fase de arranque de Herenciapp...")
    try:
        # Ejecutamos la creación de tablas de forma controlada
        init_db()
        logger.info("Base de datos sincronizada: Tablas verificadas exitosamente.")
    except Exception as e:
        logger.critical(
            f"¡Alerta en la cocina! Falla crítica al inicializar la base de datos en producción: {str(e)}",
            exc_info=True
        )
        # En producción, no queremos que el contenedor muera en silencio; 
        # dejamos que levante para poder consultar los logs vía HTTP o mantener Nginx estable
    
    yield
    logger.info("Apagando fuegos: Limpiando recursos de Herenciapp.")

app = FastAPI(
    title="Herenciapp",
        version=version,
    lifespan=lifespan
)

# routers
app.include_router(api_router)  # main or system router
app.include_router(users_router) # users router

# Static Files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory="src/templates")
templates.env.globals.update(config=settings)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": version
        }
    )
