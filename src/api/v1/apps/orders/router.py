# src/api/v1/apps/orders/router.py
from fastapi import APIRouter, status, Request, Depends, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from typing import List
from src.api.v1.apps.orders.schemas import ProductCreate, ProductRead, ProductUpdate
from src.api.v1.apps.orders.services import FlavorService, MeatService, ProductService
from src.api.v1.apps.orders.schemas import FlavorCatalogueCreate, FlavorCatalogueRead, FlavorCatalogueUpdate
from src.api.v1.apps.orders.schemas import MeatCatalogueCreate, MeatCatalogueRead, MeatCatalogueUpdate
from src.api.v1.apps.orders.models import Product
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

@router.get("/products", response_class=HTMLResponse)
async def get_add_product_page(
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Renders the dedicated 'Add New Product' workspace form.
    Only allows access if valid auth tokens are found.
    """
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={
            "config": settings,
            "user": current_user # for nav_bar
        }
    )

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_new_product(product_in: ProductCreate, 
                       current_user: dict = Depends(get_current_user_from_cookie),
                       session: Session = Depends(get_session)):
    
    product_service = ProductService(session)
    return product_service.create_product(product_in)

@router.patch("/products/{product_id}", 
              response_model=ProductRead, status_code=status.HTTP_200_OK)
async def update_product(product_update: ProductUpdate,
                         product_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    product_service = ProductService(session)
    
    return product_service.update_product(product_id=product_id, product_in=product_update)

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    product_service = ProductService(session)
    
    return product_service.delete_product(product_id=product_id)

# endpoint to acces the update product template
@router.get("/products/update", response_class=HTMLResponse)
async def get_update_product_template(request: Request,
                        current_user: dict = Depends(get_current_user_from_cookie),
                        session: Session = Depends(get_session)
                        ) -> Response:
    product_service = ProductService(session)
    product_list = product_service.get_products()
    return templates.TemplateResponse(
        request=request,
        name="products_update.html",
        context={
            "config": settings,
            "products": product_list
        }
    )

@router.get("/products/{product_id}",
            response_model=ProductRead, 
            status_code=status.HTTP_200_OK)
async def get_product_by_id(
    product_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
    ) -> Product | None:
    """
    Returns an individual product information
    """

    product_service = ProductService(session)
    product = product_service.get_product_by_id(product_id=product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID index token {product_id} could not be located."
        ) 

    return product

# --- Flavors endpoints init ---
# Flavors is for selection or pick of the main_dish selection.
#
##########################################

# ui template endpoint for flavors management
@router.get("/flavors/list", response_class=HTMLResponse)
async def get_flavors_management_page(request: Request,
                        current_user: dict = Depends(get_current_user_from_cookie),
                        session: Session = Depends(get_session)
                        ) -> Response:
    flavor_service = FlavorService(session)
    flavor_list = flavor_service.get_flavors()
    return templates.TemplateResponse(
        request=request,
        name="flavors/list.html",
        context={
            "config": settings,
            "flavors": flavor_list,
            "user": current_user # for nav_bar
        }
    )

# ui template endpoint for flavors additon
@router.get("/flavors/add", response_class=HTMLResponse)
async def add_flavors_page(request: Request,
                        current_user: dict = Depends(get_current_user_from_cookie),
                        session: Session = Depends(get_session)
                        ) -> Response:
    # add the context for products
    products_list = ProductService(session).get_products()
    return templates.TemplateResponse(
        request=request,
        name="flavors/create.html",
        context={
            "config": settings,
            "user": current_user,
            "products": products_list
        }
    )

@router.post("/flavors", response_model=FlavorCatalogueRead, status_code=status.HTTP_201_CREATED)
def create_new_flavor(flavor_in: FlavorCatalogueCreate, 
                      current_user: dict = Depends(get_current_user_from_cookie),
                      session: Session = Depends(get_session)):
    
    flavor_service = FlavorService(session)
    return flavor_service.create_flavor(flavor_in=flavor_in)

@router.patch("/flavors/{flavor_id}", 
              response_model=FlavorCatalogueRead, status_code=status.HTTP_200_OK)
async def update_flavor(flavor_update: FlavorCatalogueUpdate,
                         flavor_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    flavor_service = FlavorService(session)
    
    return flavor_service.update_flavor(flavor_id=flavor_id, flavor_in=flavor_update)

@router.delete("/flavors/{flavor_id}")
async def delete_flavor(flavor_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    flavor_service = FlavorService(session)
    
    return flavor_service.delete_flavor(flavor_id=flavor_id)

@router.get("/flavors/{id}", 
            response_model=FlavorCatalogueRead, 
            status_code=status.HTTP_200_OK)
async def get_flavor_by_id(
    id: int,
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
    ) -> FlavorCatalogueRead | None:
    """
    Returns an individual flavor information
    """

    flavor_service = FlavorService(session)
    flavor = flavor_service.get_flavor_by_id(flavor_id=id)

    if not flavor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flavor with ID index {id} could not be located."
        ) 

    return flavor

######### --- Flavors endpoints end --- ##############



##########  --- Meat catalogue endpoints init --- ##############

@router.post("/flavors/meat", response_model=MeatCatalogueRead, status_code=status.HTTP_201_CREATED)
def create_new_meat(meat_in: MeatCatalogueCreate, 
                    current_user: dict = Depends(get_current_user_from_cookie),
                    session: Session = Depends(get_session)):
    
    meat_service = MeatService(session)
    return meat_service.create_meat(meat_in=meat_in)


# general endpoint go first, then the specifics
@router.get("/flavors/meat/all", response_model=List[MeatCatalogueRead], status_code=status.HTTP_200_OK)
async def get_meat_all(
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
) -> List[MeatCatalogueRead]:
    """
    Returns all meat in the catalogue as JSON
    """
    meat_service = MeatService(session)
    meat_list = meat_service.get_meat_catalogue()

    # If the service returns None or an empty list, raise the 404
    if not meat_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meat catalogue is empty."
        ) 

    return meat_list


@router.get("/flavors/meat/{id}", 
            response_model=MeatCatalogueRead, 
            status_code=status.HTTP_200_OK)
async def get_meat_by_id(
    id: int,
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
    ) -> MeatCatalogueRead | None:
    """
    Returns an individual meat information
    """

    meat_service = MeatService(session)
    meat = meat_service.get_meat_by_id(meat_id=id)

    if not meat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meat with ID index {id} could not be located."
        ) 

    return meat

@router.patch("/flavors/meat/{meat_id}", 
              response_model=MeatCatalogueRead, status_code=status.HTTP_200_OK)
async def update_meat(meat_update: MeatCatalogueUpdate,
                      meat_id: int, 
                      current_user: dict = Depends(get_current_user_from_cookie),
                      session: Session = Depends(get_session)
                         ):
    
    meat_service = MeatService(session)
    
    return meat_service.update_meat(meat_id=meat_id, meat_in=meat_update)

@router.delete("/flavors/meat/{meat_id}")
async def delete_meat(meat_id: int, 
                       current_user: dict = Depends(get_current_user_from_cookie),
                       session: Session = Depends(get_session)
                         ):
    
    meat_service = MeatService(session)
    
    return meat_service.delete_meat(meat_id=meat_id)