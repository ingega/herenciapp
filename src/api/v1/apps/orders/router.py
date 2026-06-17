# src/api/v1/apps/orders/router.py
from fastapi import APIRouter, status, Request, Depends, HTTPException, Response
from fastapi.responses import Response, HTMLResponse, RedirectResponse


from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from typing import List

# schemas
from src.api.v1.apps.orders.schemas import OrderDetailReadNested, ProductCreate, ProductRead, ProductUpdate
from src.api.v1.apps.orders.schemas import FlavorCatalogueCreate, FlavorCatalogueRead, FlavorCatalogueUpdate
from src.api.v1.apps.orders.schemas import MeatCatalogueCreate, MeatCatalogueRead, MeatCatalogueUpdate
from src.api.v1.apps.orders.schemas import OrderCreate, OrderRead, OrderUpdate, OrderDetailCreate
from src.api.v1.apps.orders.schemas import OrderDetailResponse, OrderDiscount, OrderClose

# models
from src.api.v1.apps.orders.models import Product, Order, mexico_time_filter

# services
from src.api.v1.apps.orders.services import FlavorService, MeatService, ProductService
from src.api.v1.apps.orders.services import OrderService, MeatService

# functions, database, auth
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.database import get_session

# authz importation
from src.api.v1.authz.authz import RoleChecker

# routers
router = APIRouter(prefix="/orders", tags=["orders"], redirect_slashes=False)
router_products = APIRouter(prefix="/orders/products", tags=["products"], redirect_slashes=False)
router_flavors = APIRouter(prefix="/orders/flavors", tags=["flavors"], redirect_slashes=False)
router_meat = APIRouter(prefix="/orders/flavors/meat", tags=["meat"], redirect_slashes=False)

templates = Jinja2Templates(directory="src/templates")
templates.env.filters["mexico_time"] = mexico_time_filter

# authz role checker
allow_admin = RoleChecker(["admin"])
allow_user = RoleChecker(["admin", "user"])

# dependencies for service injection
def get_order_service(session: Session = Depends(get_session)) -> OrderService:
    return OrderService(session)

def get_product_service(session: Session = Depends(get_session)) -> ProductService:
    return ProductService(session)

def get_flavor_service(session: Session = Depends(get_session)) -> FlavorService:
    return FlavorService(session)

def get_meat_service(session: Session = Depends(get_session)) -> MeatService:
    return MeatService(session)


#### --- orders endpoints --- ###

# templates endpoints first

# main orders creation template
@router.get("/create-ticket", 
            dependencies=[Depends(allow_user)],
            response_class=HTMLResponse)
def render_order_creation_workspace(
    request: Request,
    product_service: ProductService = Depends(get_product_service),
    flavor_service: FlavorService = Depends(get_flavor_service),
    meat_service: MeatService = Depends(get_meat_service), # Dynamic meat injection
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    UI VIEW: Serves the ticket workspace. Dynamically pulls active 
    products, explicit flavors, and the database-backed meat catalogue.
    """
    all_products = product_service.get_products()
    all_flavors = flavor_service.get_flavors()
    
    # FETCH DIRECTLY FROM YOUR LIVE DATABASE SERVICE SPRINT!
    db_meat_catalogue = meat_service.get_meat_catalogue()

    return templates.TemplateResponse(
        request=request,
        name="orders/create.html",
        context={
            "config": settings,
            "products": all_products,
            "flavors": all_flavors,
            "meat_catalogue": db_meat_catalogue,
            "current_user": current_user # for nav_bar
        }
    )

# kitchen-dashboard
@router.get("/kitchen/dashboard", response_class=HTMLResponse)
def get_kitchen_orders(
    request: Request,                   
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    return templates.TemplateResponse(
        request=request,
        name="orders/kitchen/dashboard.html",
        context={
            "config": settings,
            "current_user": current_user # for nav_bar
        }
    )

# kitchen-dashboard-cards
@router.get("/kitchen/cards", response_class=HTMLResponse)
async def get_kitchen_cards(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)):
    
    db_orders = order_service.get_all_orders_sended()
    active_orders = [OrderDetailResponse.model_validate(order) for order in db_orders]
    return templates.TemplateResponse(
        request=request,
        name="orders/kitchen/cards.html",
        context={
            "config": settings,
            "active_orders": active_orders,
            "current_user": current_user # for nav_bar
        }
    )

# waiter-dashboard
@router.get("/waiter/dashboard", response_class=HTMLResponse)
def get_waiter_orders(
    request: Request,                   
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    return templates.TemplateResponse(
        request=request,
        name="orders/waiter/dashboard.html",
        context={
            "config": settings,
            "current_user": current_user # for nav_bar
        }
    )

# waiter-dashboard-cards
@router.get("/waiter/cards", response_class=HTMLResponse)
async def get_waiter_cards(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)):
    
    db_orders = order_service.get_all_orders_delivered()
    active_orders = [OrderDetailResponse.model_validate(order) for order in db_orders]
    return templates.TemplateResponse(
        request=request,
        name="orders/waiter/cards.html",
        context={
            "config": settings,
            "active_orders": active_orders,
            "current_user": current_user # for nav_bar
        }
    )

# close order template
@router.get("/{order_id}/checkout-form", 
            dependencies=[Depends(allow_user)],
            response_class=HTMLResponse)
def get_checkout_template(
    order_id: int,
    request: Request,
    service: OrderService = Depends(get_order_service),                   
    current_user: dict = Depends(get_current_user_from_cookie)
    ):
    # retrieve order data
    order = service.get_order_by_id(order_id)
    
    return templates.TemplateResponse(
        request=request,
        name="orders/check_out.html",
        context={
            "config": settings,
            "order": order,
            "current_user": current_user # for nav_bar
        }
    )

# sub-function to update the discount
@router.patch("/{order_id}/discount",
              dependencies=[Depends(allow_user)], 
              response_class=HTMLResponse, tags=["waiter"])
def order_discount(
    request: Request,
    order_id: int,
    payload: OrderDiscount = Depends(OrderDiscount.as_form), # for htpx 
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Endpoint for update the discuount and return data for card in HTMX"""
    
    # Execute the query
    result, code = service.update_order_discount(order_id, payload=payload)
    
    if not result:
        raise HTTPException(status_code=code, detail="data could not be updated")
        
    # We need to resend the updated data
    updated_order = service.get_order_by_id(order_id)
    
    # Retornamos directamente el fragmento de la card para que HTMX haga el swap atómico
    return templates.TemplateResponse(
        request=request,
        name="orders/waiter/cards.html",
        context={
            "config": settings,
            "active_orders": [updated_order],
            "current_user": current_user # for nav_bar
        }
    )

# close an order
@router.patch("/{order_id}/closed", 
              response_model=Order,
              dependencies=[Depends(allow_user)],
              status_code=status.HTTP_200_OK, 
              tags=["waiter"])
def order_closed(
    order_id: int,
    response: Response,
    payload: OrderClose,  
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    service.close_order(order_id=order_id, checkout_payload=payload)
    # return a redirect
    response.headers["HX-Redirect"] = "/orders/waiter/dashboard"
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# list of active orders
@router.get("/", response_class=HTMLResponse)
def view_active_orders_dashboard(
    request: Request,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Renders the active operational POS screen tracking all unclosed (open) tables,
    showing their live balances and running times using Local OS times.
    """
    active_orders = service.get_active_orders()

    return templates.TemplateResponse(
        request=request,
        name="orders/dashboard.html",
        context={
            "config": settings,
            "orders": active_orders,
            "current_user": current_user # for nav_bar
        }
    )

# add an order (API)
@router.post("/create", response_model=OrderRead,
             dependencies=[Depends(allow_user)], 
             status_code=status.HTTP_201_CREATED)
def api_open_new_table_ticket(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Initializes an order entity, stamps the waiter's user_id, 
    processes any initial payload items, and commits with local system timestamps.
    """
    return service.create_order(user_id=current_user['user_id'], order_in=payload)

@router.patch("/update/{order_id}", response_model=OrderRead)
def api_patch_order_attributes(
    order_id: int,
    payload: OrderUpdate,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Modifies top-level order properties (discounts, seat expansion, tips) 
    and applies math recalculated ledgers dynamically.
    """
    return service.update_order(order_id=order_id, order_in=payload)

@router.delete("/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_void_entire_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Voids out an open ticket from the active ledger permanently.
    """
    service.delete_order(order_id)
    return None

@router.get("/{order_id}", response_model=OrderRead)
def api_get_order_by_id(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Retrieves a single order by its unique identifier, including all nested items.
    """
    order = service.get_order_by_id(order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} could not be located."
        ) 
    return order

@router.get("/all/", response_model=List[OrderRead])
def api_get_all_orders(
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Retrieves all orders in the system, including nested items.
    """
    return service.get_orders()

# -- nested items in order endpoints ---

# items dispatched
@router.post("/items/{item_id}/dispatch")
async def api_dispatch_kitchen_item(
    item_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user_from_cookie),
    # Inject your service class context instance here
    service: OrderService = Depends(get_order_service) 
    ):
    """
    Endpoint targeted by HTMX to clear an item line from the active board.
    Returns the newly computed HTML cards partial view grid.
    """
    # Execute the database update routine
    success = service.dispatch_order_item(item_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not update item status")
        
    # Re-fetch active tickets utilizing our lightning fast memory filter layout
    active_orders = service.get_all_orders_sended()
    
    # Return a redirect to dashboard to refresh the values
    return RedirectResponse(url="/orders/kitchen/dashboard")

@router.get("/items/all/", response_model=List[OrderDetailReadNested], tags=["Items"])
def api_get_all_items_for_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Retrieves all items for a given order, including nested product and flavor details.
    """
    return service.get_all_items_for_order(order_id=order_id)

# this endpoint add or updated an item if already exists
@router.post("/{order_id}/items", 
             response_model=OrderDetailResponse,
             status_code=status.HTTP_201_CREATED, 
             tags=["Items"])
def api_append_item_to_ticket(
    order_id: int,
    item_payload: OrderDetailCreate,
    response: Response,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Pushes a new item onto a ticket. If matching combinations (product, flavor, seat)
    exist on an unsent ticket, it sums quantities dynamically in memory to prevent table pollution.
    """
    # it is new item or updated item?
    db_order, is_new_item = service.add_or_update_item(order_id=order_id, item_in=item_payload)
    if not is_new_item:
        response.status_code = status.HTTP_200_OK
    else: # mean new item
        status_updated = service.change_sended_status(order_id)
        if not status_updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Order ticket with ID {order_id} could not be found."
            )
    
    return db_order

@router.delete("/delete/{order_id}/items/{item_id}", 
               response_model=OrderRead, tags=["Items"])
def api_remove_item_from_ticket(
    order_id: int,
    item_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    REST API: Voids a row out of an open ticket. Blocked if the kitchen has already flag-locked 
    the preparation process.
    """
    return service.delete_item(order_id=order_id, item_id=item_id)

########## --- products endpoints --- ###########################

#################################################################
# this endpoints need authz
@router_products.get("/", response_class=HTMLResponse,
                     dependencies=[Depends(allow_admin)])
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
            "current_user": current_user # for nav_bar
        }
    )

@router_products.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_new_product(product_in: ProductCreate, 
                       current_user: dict = Depends(get_current_user_from_cookie),
                       session: Session = Depends(get_session)):
    
    product_service = ProductService(session)
    return product_service.create_product(product_in)

@router_products.patch("/{product_id}", 
              response_model=ProductRead, status_code=status.HTTP_200_OK)
async def update_product(product_update: ProductUpdate,
                         product_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    product_service = ProductService(session)
    
    return product_service.update_product(product_id=product_id, product_in=product_update)

@router_products.delete("/{product_id}")
async def delete_product(product_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    product_service = ProductService(session)
    
    return product_service.delete_product(product_id=product_id)

# endpoint to acces the update product template
@router_products.get("/update", response_class=HTMLResponse)
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
            "products": product_list,
            "current_user": current_user # for nav_bar
        }
    )

@router_products.get("/{product_id}",
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

@router_products.get("/all/", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
async def get_all_products(
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
): 
    """
    Returns all products in the catalogue as JSON
    """
    product_service = ProductService(session)
    product_list = product_service.get_products()
    # debug propouse, delete on production.
    print(f"Debug: Retrieved product list: {product_list}")  # Debug statement

    # If the service returns None or an empty list, raise the 404
    if not product_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product catalogue is empty."
        ) 

    return product_list

# --- Flavors endpoints init ---
# Flavors is for selection or pick of the main_dish selection.
#
##########################################

# ui template endpoint for flavors management
@router_flavors.get("/list", response_class=HTMLResponse)
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
            "current_user": current_user # for nav_bar
        }
    )

# ui template endpoint for flavors additon
@router_flavors.get("/add", response_class=HTMLResponse,
                    dependencies=[Depends(allow_admin)])
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
            "current_user": current_user,
            "products": products_list
        }
    )

@router_flavors.post("/", response_model=FlavorCatalogueRead, status_code=status.HTTP_201_CREATED)
def create_new_flavor(flavor_in: FlavorCatalogueCreate, 
                      current_user: dict = Depends(get_current_user_from_cookie),
                      session: Session = Depends(get_session)):
    
    flavor_service = FlavorService(session)
    return flavor_service.create_flavor(flavor_in=flavor_in)

@router_flavors.patch("/{flavor_id}", 
              response_model=FlavorCatalogueRead, status_code=status.HTTP_200_OK)
async def update_flavor(flavor_update: FlavorCatalogueUpdate,
                         flavor_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    flavor_service = FlavorService(session)
    
    return flavor_service.update_flavor(flavor_id=flavor_id, flavor_in=flavor_update)

@router_flavors.delete("/{flavor_id}")
async def delete_flavor(flavor_id: int, 
                         current_user: dict = Depends(get_current_user_from_cookie),
                         session: Session = Depends(get_session)
                         ):
    
    flavor_service = FlavorService(session)
    
    return flavor_service.delete_flavor(flavor_id=flavor_id)

@router_flavors.get("/{id}", 
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

@router_flavors.get("/all/", response_model=List[FlavorCatalogueRead], 
                    status_code=status.HTTP_200_OK)
async def get_flavors_all(
    current_user: dict = Depends(get_current_user_from_cookie),
    session: Session = Depends(get_session)
) -> List[FlavorCatalogueRead]:
    """
    Returns all flavors in the catalogue as JSON
    """
    flavor_service = FlavorService(session)
    flavor_list = flavor_service.get_flavors()

    # If the service returns None or an empty list, raise the 404
    if not flavor_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flavor catalogue is empty."
        ) 

    return flavor_list

######### --- Flavors endpoints end --- ##############



##########  --- Meat catalogue endpoints init --- ##############

# ui template endpoint for meat catalogue management
@router_meat.get("/add/ui", response_class=HTMLResponse, 
                 dependencies=[Depends(allow_admin)],
                 status_code=status.HTTP_200_OK)
async def get_meat_add_page(request: Request,
                           current_user: dict = Depends(get_current_user_from_cookie),
                           session: Session = Depends(get_session)
                           ) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="meat/create.html",
        context={
            "config": settings,
            "current_user": current_user
        }
    )

@router_meat.post("/add", response_model=MeatCatalogueRead, 
                  dependencies=[Depends(allow_user)],
                  status_code=status.HTTP_201_CREATED)
def create_new_meat(meat_in: MeatCatalogueCreate, 
                    current_user: dict = Depends(get_current_user_from_cookie),
                    session: Session = Depends(get_session)):
    
    meat_service = MeatService(session)
    return meat_service.create_meat(meat_in=meat_in)

# ui template endpoint for meat catalogue management
@router_meat.get("/list", response_class=HTMLResponse)
async def get_meat_management_page(request: Request,
                        current_user: dict = Depends(get_current_user_from_cookie),
                        session: Session = Depends(get_session)
                        ) -> Response:
    meat_service = MeatService(session)
    meat_list = meat_service.get_meat_catalogue()
    print(meat_list)
    return templates.TemplateResponse(
        request=request,
        name="meat/list.html",
        context={
            "config": settings,
            "meat_list": meat_list,
            "current_user": current_user # for nav_bar
        }
    )

# general endpoint go first, then the specifics
@router_meat.get("/all", response_model=List[MeatCatalogueRead], status_code=status.HTTP_200_OK)
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

@router_meat.get("/{id}", 
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

@router_meat.patch("/{meat_id}", 
              response_model=MeatCatalogueRead,
              dependencies=[Depends(allow_user)], 
              status_code=status.HTTP_200_OK)
async def update_meat(meat_update: MeatCatalogueUpdate,
                      meat_id: int, 
                      current_user: dict = Depends(get_current_user_from_cookie),
                      session: Session = Depends(get_session)
                         ):
    
    meat_service = MeatService(session)
    
    return meat_service.update_meat(meat_id=meat_id, meat_in=meat_update)

@router_meat.delete("/{meat_id}", dependencies=[Depends(allow_user)])
async def delete_meat(meat_id: int, 
                       current_user: dict = Depends(get_current_user_from_cookie),
                       session: Session = Depends(get_session)
                         ):
    
    meat_service = MeatService(session)
    
    return meat_service.delete_meat(meat_id=meat_id)