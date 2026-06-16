# src/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import date
from src.api.v1.apps.orders.services import OrderService
from src.api.v1.apps.orders.schemas import OrderDetailResponse
from src.database import get_session

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

@api_router.get("/playground", status_code=200)
def get_playground(session: Session = Depends(get_session)):
    """
    This space is for test new endpoints or functions
    """
    order_service = OrderService(session)
    db_orders = order_service.total_day_sales(target_date=date(2026,6,15))

    return db_orders
