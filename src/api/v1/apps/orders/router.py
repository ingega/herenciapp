# src/api/v1/apps/orders/router.py
from fastapi import APIRouter, status, Request, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["orders"])

templates = Jinja2Templates(directory="src/templates")

@router.get("/orders")
async def get_orders(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        status_code=status.HTTP_200_OK,
        context={'details': "This is the orders page."}
    )