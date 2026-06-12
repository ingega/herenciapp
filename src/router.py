# src/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
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
    db_orders = order_service.get_all_orders_sended()

    active_orders = [OrderDetailResponse.model_validate(order) for order in db_orders]

    return active_orders
