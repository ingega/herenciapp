# src/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.api.v1.apps.orders.services import ItemService
from src.api.v1.apps.orders.schemas import OrderDetailAddItem, OrderDetailRead
from src.database import get_session

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

@api_router.post("/playground", status_code=200)
def post_playground(payload:OrderDetailAddItem,
                    session:Session=Depends(get_session),
                   ) -> OrderDetailRead:
    """
    This space is for test new endpoints or functions
    """
    item_service = ItemService(session=session)
    return  item_service.create_item(item_in=payload)

@api_router.get("/playground", status_code=200)
def get_playground(order_id: int,
                    session:Session=Depends(get_session),
                   ):
    """
    This space is for test new endpoints or functions
    """
    item_service = ItemService(session=session)
    return  item_service.get_order_items(order_id=order_id)
