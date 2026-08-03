# src/api/v1/apps/orders/schemas.py
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from fastapi import Form
from pydantic import Field, condecimal
from sqlmodel import SQLModel, Field, SmallInteger, Text

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
    price: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)


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
    selection: str = Field(default="standar")
    quantity: int = Field(default=1)
    notes: Optional[str] = None
    extra_charge: condecimal(max_digits=5, decimal_places=2) = Field(default=0.00)


class OrderDetailCreate(OrderDetailBase):
    """Used when adding an item to an active or new order."""
    pass

class OrderDetailAddItem(OrderDetailBase):
    """Used when adding an item to an active order, not new."""
    order_id: int

class OrderDetailUpdateItem(SQLModel):
    order_id: Optional[int] = Field(foreign_key="orders.id", index=True)
    person_number: Optional[int] = Field(sa_type=SmallInteger(), default=1, index=True)
    product_id: Optional[int] = Field(foreign_key="products.id")
    flavor_id: Optional[int] = Field(foreign_key="flavor_catalogue.id")
    selection: Optional[str] = Field(max_length=50, default=None)
    quantity: Optional[int] = Field(default=1, sa_type=SmallInteger())
    notes: Optional[str] = Field(default=None, sa_type=Text())


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
    discount: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)
    discount_motive: Optional[str] = None
    tip: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)
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
    discount: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    discount_motive: Optional[str] = None
    tip: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    pay_method: Optional[PayMethod] = None


class OrderSend(SQLModel):
    """Pushes items to Step 3: Kitchen Queued Queue."""
    sended: bool = True


class OrderClose(SQLModel):
    """Final step to close table out and process final billing math safely."""
    pay_method: PayMethod
    tip: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)


class OrderDiscount(SQLModel):
    """Schema to add a discount to an order"""
    discount: Decimal = Field(default=0.00, max_digits=6, decimal_places=2)
    discount_motive: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        discount: Decimal = Form(default=0.00),
        discount_motive: Optional[str] = Form(None)
    ):
        return cls(discount=discount, discount_motive=discount_motive)


class OrderRead(OrderBase):
    id: int
    user_id: int  # Waiter ID track
    created_at: datetime
    delivered_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sended: bool
    closed: bool
    total: condecimal(max_digits=10, decimal_places=2)


class OrderDetailResponse(OrderRead):
    """
    The ultimate serialization master payload.
    Returns the complete layout structure with nested structural calculations.
    """
    items: List[OrderDetailReadNested] = []


OrderDetailResponse.model_rebuild()

# =========================================
# Order batch schemas for items
# =========================================

class OrderItemBatchInput(SQLModel):
    id: Optional[str] = None  # Existing ID or temporary client ID ('new_12345')
    product_id: int
    flavor_id: int
    selection: Optional[str] = ""
    quantity: int = 1
    person_number: int = 1

class OrderBatchUpdateSchema(SQLModel):
    items: List[OrderItemBatchInput] = []

# ==========================================
# 1. MEAT CATALOGUE SCHEMAS
# ==========================================


class MeatCatalogueBase(SQLModel):
    description: str = Field(max_length=50)


class MeatCatalogueCreate(MeatCatalogueBase):
    pass


class MeatCatalogueRead(MeatCatalogueBase):
    id: int


class MeatCatalogueUpdate(SQLModel):
    description: Optional[str] = Field(default=None, max_length=50)