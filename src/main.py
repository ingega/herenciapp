# src/main.py
import logging
from contextlib import asynccontextmanager
import pathlib
from fastapi import FastAPI, Request, status, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from datetime import datetime

# config
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.__init__ import __version__ as version
from .database import init_db, get_session
# routers
from src.router import api_router
from .api.v1.apps.users.router import router as users_router
from .api.v1.auth.router import router as auth_router
from .api.v1.apps.orders.router import router as orders_router
from .api.v1.apps.orders.router import router_flavors, router_meat, router_products
# services
from .api.v1.apps.orders.services import OrderService

# logger config
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
    Smart exception handler. 
    If the request comes from an AJAX fetch (JSON/POST), it passes the raw status code.
    If it's a page navigation (GET), it redirects cleanly based on Auth status.
    """
    # 1. Check if the request is an asynchronous data submission
    if request.method in ["POST", "PUT", "PATCH", "DELETE"] or "application/json" in request.headers.get("accept", "").lower():
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "detail": exc.detail}
        )
    
    # 2. Fallback for standard UI browser tabs (GET requests)
    
    # Scenario A: User is NOT logged in or session expired (401) -> Go to Login
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        return response

    # Scenario B: User IS logged in but lacks required Role Permissions (403) -> Redirect back to Main Dashboard
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        logger.warning(f"Authorization failure: User tried accessing {request.url.path} without proper privileges.")
        # Redirecting to /main avoids breaking their valid login session!
        return RedirectResponse(url="/main", status_code=status.HTTP_303_SEE_OTHER)

    # General catch-all fallback for other page routing issues (e.g., 404, 500)
    return RedirectResponse(url="/main" if request.cookies.get("access_token") else "/auth/login", status_code=status.HTTP_303_SEE_OTHER)

# routers
app.include_router(api_router)  # main or system router
app.include_router(users_router) # users router
app.include_router(auth_router) # auth router
app.include_router(orders_router) # orders router
app.include_router(router_flavors) # flavors router
app.include_router(router_meat) # meat router
app.include_router(router_products) # products router

# Static Files
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
STATIC_DIR = CURRENT_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="src/templates")
templates.env.globals.update(config=settings)

# Authenticated user main page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """When the root URL is reached, we need to check if
    the user is authenticated. If they are, we redirect them to the main dashboard.
    """
    current_user = request.cookies.get("access_token")
    if current_user:
        return RedirectResponse(url="/main", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": version
        }
    )

# Authenticated user main page
@app.get("/main")
async def main(request: Request,
               session: Session = Depends(get_session), 
               current_user: dict = Depends(get_current_user_from_cookie)):
    # the page needs the active orders
    active_orders = OrderService(session).get_active_orders()

    return templates.TemplateResponse(
        request=request,
        name="main.html",
        context={
            "config": settings,
            "active_orders": active_orders,
            "current_user": current_user  # current user data from the JWT payload
        }
    )

# logout endpoint to clear the auth cookie and redirect to root
@app.get("/logout")
async def logout(response: Response):
    # Create a redirection response pointing back to root
    redirect_response = RedirectResponse(url="/", status_code=303)
    
    # Explicitly delete the cookie
    redirect_response.delete_cookie(
        key="access_token", 
        path="/",
        httponly=True,
        samesite="lax"
    )
    
    return redirect_response
