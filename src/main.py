# src/main.py
import logging
from contextlib import asynccontextmanager
import pathlib
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.router import api_router
from src.__init__ import __version__ as version
from .database import init_db
from .api.v1.apps.users.router import router as users_router
from .api.v1.auth.router import router as auth_router

# Configuración del logger oficial de producción para el EC2
logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        logging.log(logging.ERROR, f"[LIFESPAN CRITICAL] init raise an exception: {str(e)}")
    yield

app = FastAPI(
    title="Herenciapp",
        version=version,
    lifespan=lifespan
)

# avoid return sensitive information in validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # We just return a generic message without the details of the validation errors to avoid 
    # leaking sensitive information about the server's internals or the expected data format. 
    # This is a security best practice in production environments.
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error: Invalid data provided, review the format."}
    )

# Custom exception handler for HTTPException to handle 401 Unauthorized globally
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Interceptors exceptions. If a 401 occurs on a page request, 
    it wipes any bad cookie and sends the user back to the login gate.
    """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Clear the invalid cookie and route them to your auth/login page view
        response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        return response
        
    # Fallback for other standard HTTP exceptions (like 404, 500, etc.)
    # If your app has custom templates for those, you can render them here.
    return RedirectResponse(url="/auth/login")

# routers
app.include_router(api_router)  # main or system router
app.include_router(users_router) # users router
app.include_router(auth_router) # auth router

# Static Files
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
STATIC_DIR = CURRENT_DIR / "static"

# debug propurposes: check if static dir exists and log the result
if STATIC_DIR.exists() and STATIC_DIR.is_dir():
    logger.info(f"Static directory found at: {STATIC_DIR}")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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

@app.get("/main")
async def main(request: Request, 
               current_user: dict = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={
            "config": settings,
            "current_user": current_user  # current user data from the JWT payload
        }
    )
