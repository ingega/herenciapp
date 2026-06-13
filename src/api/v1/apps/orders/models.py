# src/api/v1/apps/orders/models.py
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum
from typing import List, Optional
from pydantic import condecimal
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint
from sqlalchemy import SmallInteger, Text

# system must use the MEXICO CITY CST TIME, but in future we can add a env var in config
MEXICO_TZ = ZoneInfo("America/Mexico_City")

def get_mexico_time() -> datetime:
    """
    Guarantees that regardless of whether this code executes locally or inside an
    AWS Linux EC2/Docker host configured to UTC, it returns true Mexico City time.
    """
    return datetime.now(MEXICO_TZ)


class PayMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    CRYPTO = "crypto"
    MIXED = "mixed"  # For orders paid with multiple methods (e.g., part cash, part card)


class ItemPrepStatus(str, Enum):
    QUEUED = "queued"       # Step 3: Chef receives it
    COOKING = "cooking"     # Chef is working on it
    READY = "ready"         # Step 4: Chef notices waiter
    PARTIAL_DELIVERED = "partial_delivered" # Step 5: Waiter delivers to customer (some items may be ready while others are still cooking)
    DELIVERED = "delivered" # Step 5: order completely delivered to customer


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)  # Associated waiter
    table_no: int = Field(sa_type=SmallInteger(), index=True, default=0)
    number_of_persons: int = Field(sa_type=SmallInteger(), default=1)

    # Combined date & time with default to current timestamp in UTC/CST mapping
    created_at: datetime = Field(default_factory=get_mexico_time, index=True)
    delivered_at: datetime = Field(default_factory=get_mexico_time, index=True)
    closed_at: datetime = Field(default_factory=get_mexico_time, index=True)
    
    # Workflow control flags
    sended: bool = Field(default=False, index=True)
    closed: bool = Field(default=False, index=True)
    
    # Financial fields using precise Decimal tracking to prevent floating-point rounding errors
    total: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)
    discount: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)
    discount_motive: Optional[str] = Field(default=None, sa_type=Text())
    tip: condecimal(max_digits=6, decimal_places=2) = Field(default=0.00)
    pay_method: Optional[PayMethod] = Field(default=None)

    # Relationships
    items: List["OrderDetail"] = Relationship(back_populates="order")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    main_dish: str = Field(max_length=50, index=True, unique=True)  # e.g., taco, burger, soda
    category: str = Field(max_length=30, index=True)  # package, taco, beverage
    price: condecimal(max_digits=6, decimal_places=2) = Field()

    # Relationships
    flavors: List["FlavorCatalogue"] = Relationship(back_populates="product")
    order_details: List["OrderDetail"] = Relationship(back_populates="product")


class FlavorCatalogue(SQLModel, table=True):
    __tablename__ = "flavor_catalogue"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    description: str = Field(max_length=50)  # Chicken, Pepperoni, Veggie, Diet Coke

    __table_args__ = (
        UniqueConstraint("product_id", "description", name="uq_product_flavor_description"),
    )

    # Relationships
    product: Product = Relationship(back_populates="flavors")
    order_details: List["OrderDetail"] = Relationship(back_populates="flavor")


class OrderDetail(SQLModel, table=True):
    __tablename__ = "order_detail"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    person_number: int = Field(sa_type=SmallInteger(), default=1, index=True)  # Tracks your Person 1, Person 2 logic!
    product_id: int = Field(foreign_key="products.id")
    flavor_id: int = Field(foreign_key="flavor_catalogue.id")
    selection: str | None = Field(max_length=50, default=None)
    quantity: int = Field(default=1, sa_type=SmallInteger())
    notes: Optional[str] = Field(default=None, sa_type=Text())
    
    # Controls steps 3, 4, 5 of your restaurant flow per item
    prep_status: ItemPrepStatus = Field(default=ItemPrepStatus.QUEUED, index=True)

    # additional financial fields for item-level additions or modifications
    extra_charge: condecimal(max_digits=5, decimal_places=2) = Field(default=0.00)
    
    # Relationships
    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_details")
    flavor: FlavorCatalogue = Relationship(back_populates="order_details")

class MeatCatalogue(SQLModel, table=True):
    __tablename__ = "meat_catalogue"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=50, unique=True)  # Chicken, Beef, Pork, Veggie