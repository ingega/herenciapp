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
    print("===================================================", flush=True)
    print("[LIFESPAN] El contenedor de Herenciapp se está encendiendo...", flush=True)
    print(f"[LIFESPAN] Modo de Ejecución detectado: Settings.APP_MODE = '{settings.APP_MODE}'", flush=True)
    
    print("[LIFESPAN] Intentando disparar init_db()...", flush=True)
    try:
        init_db()
        print("[LIFESPAN] init_db() se ejecutó limpiamente.", flush=True)
    except Exception as e:
        print(f"[LIFESPAN CRITICAL] La inicialización tiró una excepción: {str(e)}", flush=True)
        print("[LIFESPAN CRITICAL] Mantendremos la aplicación viva para auditoría visual de logs.", flush=True)
    
    print("[LIFESPAN] Fase de arranque terminada. Listo para recibir comandas en puerto 8001.", flush=True)
    print("===================================================", flush=True)
    yield
    print("[LIFESPAN] Apagando el servidor web de Herenciapp.", flush=True)

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
