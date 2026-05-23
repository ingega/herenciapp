
import logging
from fastapi import APIRouter, Request
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
            "config": settings  # Inyectamos la instancia global de configuración
        }
    )