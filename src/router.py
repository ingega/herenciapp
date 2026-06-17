# src/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from datetime import date
from src.api.v1.apps.orders.services import OrderService
from src.api.v1.apps.orders.schemas import OrderDetailResponse
from src.database import get_session
from src.api.v1.apps.orders.models import get_mexico_time

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

@api_router.get("/playground", status_code=200)
def get_playground():
    """
    This space is for test new endpoints or functions
    """
    mx_time = get_mexico_time()

    return mx_time
