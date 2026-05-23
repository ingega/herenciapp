# src/api/v1/auth/router.py
import logging
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="src/templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "config": settings
        }
    )

@router.post("/login")
async def loggin_process(request: Request):
    # --- PLACEHOLDER ZONE ---
    # Right now, there's no auth logic or JWT generation yet.
    # We simply accept ANY submission and redirect immediately to /main.
    # ------------------------
    
    return {
        "status": "success",
        "message": "Authentication successful",
        "redirect_url": "/main"
    }