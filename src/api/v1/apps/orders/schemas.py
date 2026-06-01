# src/api/v1/apps/orders/schemas.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, condecimal
from sqlmodel import SQLModel

from src.api.v1.apps.orders.models import PayMethod, ItemPrepStatus


# ==========================================
# 1. FLAVOR CATALOGUE SCHEMAS
# ==========================================
class FlavorCatalogueBase(SQLModel):
    product_id: int
    description: str = Field(max_length=50, description="e.g., Chicken, Pepperoni, Diet Coke")


class FlavorCatalogueCreate(FlavorCatalogueBase):
    pass


class FlavorCatalogueRead(FlavorCatalogueBase):
    id: int

class FlavorCatalogueUpdate(SQLModel):
    product_id: Optional[int] = None
    description: Optional[str] = Field(default=None, max_length=50)


# ==========================================
# 2. PRODUCT SCHEMAS
# ==========================================
class ProductBase(SQLModel):
    main_dish: str = Field(max_length=50)
    category: str = Field(max_length=30, description="e.g., food, dessert, beverage")
    price: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

class ProductUpdate(SQLModel):
    main_dish: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=30)
    price: Optional[condecimal(max_digits=6, decimal_places=2)] = Field(default=None)


class ProductWithFlavors(ProductRead):
    flavors: List[FlavorCatalogueRead] = []


# ==========================================
# 3. ORDER DETAIL (ITEMS) SCHEMAS
# ==========================================
class OrderDetailBase(SQLModel):
    person_number: int = Field(default=1, description="Tracks individual customer seats")
    product_id: int
    flavor_id: int
    quantity: int = Field(default=1)
    notes: Optional[str] = None
    extra_charge: Decimal = Field(default=0.00, max_digits=5, decimal_places=2)


class OrderDetailCreate(OrderDetailBase):
    """Used when adding an item to an active or new order."""
    pass


class OrderDetailUpdateStatus(SQLModel):
    """Used by the Chef console to update items along the kitchen workflow."""
    prep_status: ItemPrepStatus


class OrderDetailRead(OrderDetailBase):
    id: int
    order_id: int
    prep_status: ItemPrepStatus


class OrderDetailReadNested(OrderDetailRead):
    """Deep nested response containing resolved product and flavor details for UI display."""
    product: ProductRead
    flavor: FlavorCatalogueRead


# ==========================================
# 4. ORDER SCHEMAS
# ==========================================
class OrderBase(SQLModel):
    table_no: int = Field(default=0)
    number_of_persons: int = Field(default=1)
    discount: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)
    discount_motive: Optional[str] = None
    tip: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)
    pay_method: Optional[PayMethod] = None


class OrderCreate(SQLModel):
    """
    Inbound validation for initial table openings.
    Items can be initially empty and pushed dynamically as customers order.
    """
    table_no: int = Field(default=0)
    number_of_persons: int = Field(default=1)
    items: List[OrderDetailCreate] = []


class OrderUpdate(SQLModel):
    """Used for patches, applying discounts, updating waitstaff fields, or adding tips."""
    table_no: Optional[int] = None
    number_of_persons: Optional[int] = None
    discount: Optional[Decimal] = None
    discount_motive: Optional[str] = None
    tip: Optional[Decimal] = None
    pay_method: Optional[PayMethod] = None


class OrderSend(SQLModel):
    """Pushes items to Step 3: Kitchen Queued Queue."""
    sended: bool = True


class OrderClose(SQLModel):
    """Final step to close table out and process final billing math safely."""
    pay_method: PayMethod
    discount: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)
    discount_motive: Optional[str] = None
    tip: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)


class OrderRead(OrderBase):
    id: int
    user_id: int  # Waiter ID track
    created_at: datetime
    delivered_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sended: bool
    closed: bool
    total: Decimal


class OrderDetailResponse(OrderRead):
    """
    The ultimate serialization master payload.
    Returns the complete layout structure with nested structural calculations.
    """
    items: List[OrderDetailReadNested] = []


# ==========================================
# 1. MEAT CATALOGUE SCHEMAS
# ==========================================
class MeatCatalogueBase(SQLModel):
    description: str = Field(max_length=50, description="e.g., maciza, lengua, cachete")


class MeatCatalogueCreate(MeatCatalogueBase):
    pass


class MeatCatalogueRead(MeatCatalogueBase):
    id: int


class MeatCatalogueUpdate(SQLModel):
    description: Optional[str] = Field(default=None, max_length=50)