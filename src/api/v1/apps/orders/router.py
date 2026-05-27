# src/api/v1/apps/orders/router.py
from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src.api.v1.apps.orders.schemas import ProductCreate, ProductRead
from src.api.v1.apps.orders.services import ProductService
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.database import get_session

router = APIRouter(tags=["orders"])

templates = Jinja2Templates(directory="src/templates")

@router.get("")
async def get_orders(request: Request, 
                     current_user: dict = Depends(get_current_user_from_cookie)
                     ) -> Response:
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

# products endpoints
@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_new_product(product_in: ProductCreate, 
                       current_user: dict = Depends(get_current_user_from_cookie),
                       session: Session = Depends(get_session)):
    # Simply pass the session into our Service engine, and let it do the lifting!
    product_service = ProductService(session)
    return product_service.create_product(product_in)