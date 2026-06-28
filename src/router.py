# src/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.api.v1.apps.orders.services import ItemService
from src.database import get_session

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

@api_router.get("/playground", status_code=200)
def get_playground(session:Session=Depends(get_session)):
    """
    This space is for test new endpoints or functions
    """
    item_service = ItemService(session=session)
    order_id = 12 # just for debug
    return  item_service.get_order_items(order_id=order_id)
