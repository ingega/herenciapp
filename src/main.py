from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from contextlib import asynccontextmanager
from src.config import settings
from src.router import api_router
from src.__init__ import __version__ as version
from .database import init_db
from .api.v1.apps.users.router import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() 
    yield
    pass

app = FastAPI(
    title="Herenciapp",
        version=version,
    lifespan=lifespan
)

# routers
app.include_router(api_router)  # main or system router
app.include_router(users_router, prefix="/api/v1") # users router with versioning prefix

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
