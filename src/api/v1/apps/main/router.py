# src/api/v1/apps/main/router.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
# models
from src.api.v1.apps.orders.models import Order, OrderDetail
# utils
from src.api.v1.apps.orders.models import mexico_time_filter 
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings

main_router = APIRouter(prefix="/main/statistics", tags=["dashboards", "statistics"])

# Jinja templates
templates = Jinja2Templates(directory="src/templates")
templates.env.filters["mexico_time"] = mexico_time_filter

# financial dashboard
@main_router.get("/", response_class=HTMLResponse, tags="statistics")
def get_financial_dashboard(
        request: Request,
        current_user: dict = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        request=request,
        name="main/financial_dashboard.html",
        context={
            "config": settings,
            "current_user": current_user # for nav_bar
        }
    )

