# src/api/v1/apps/main/router.py
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from datetime import date

# settings, config, auth, authz 
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.database import get_session
from src.api.v1.authz.authz import RoleChecker
# utils
from src.api.v1.apps.orders.models import mexico_time_filter
# services
from src.api.v1.apps.main.services import FinancialService

main_router = APIRouter(prefix="/main/statistics", tags=["dashboards", "statistics"])

# Jinja templates
templates = Jinja2Templates(directory="src/templates")
templates.env.filters["mexico_time"] = mexico_time_filter

# Services dependencies
def get_financial_service(session: Session=Depends(get_session)):
    return FinancialService(session)

# authz
allow_admin = RoleChecker(["admin"])

# auxiliar template
@main_router.get("/", response_class=HTMLResponse, dependencies=[Depends(allow_admin)])
def select_statistics_date_view(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Renders the single form entry screen for picking an audit day."""
    return templates.TemplateResponse(
        request=request,
        name="main/statistics_entry.html",
        context={
            "config": settings,
            "current_user": current_user
        }
    )

# financial dashboard
@main_router.get("/{date}", 
                 response_class=HTMLResponse, 
                 dependencies=[Depends(allow_admin)],
                 status_code=status.HTTP_200_OK,
                 tags=["statistics"])
def get_financial_dashboard(
        date: date,
        request: Request,
        financial_service: FinancialService=Depends(get_financial_service),
        current_user: dict = Depends(get_current_user_from_cookie)
):
    # retrieve data
    data = financial_service.get_totals_per_date(date)
    return templates.TemplateResponse(
        request=request,
        name="main/financial_dashboard.html",
        context={
            "config": settings,
            "data": data,
            "current_user": current_user # for nav_bar
        }
    )

