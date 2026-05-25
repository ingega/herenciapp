# src/api/v1/apps/orders/router.py
from fastapi import APIRouter, status, Request, Depends
from fastapi.templating import Jinja2Templates
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings

router = APIRouter(tags=["orders"])

templates = Jinja2Templates(directory="src/templates")

@router.get("/")
async def get_orders(request: Request, 
                     current_user: dict = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        status_code=status.HTTP_200_OK,
        context={
            "config": settings,
            "user": current_user, 
            "details": "This is the orders page."
            }
    )