# src/api/v1/apps/orders/services.py

from datetime import datetime
from typing import List
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.api.v1.apps.orders.models import FlavorCatalogue, MeatCatalogue, Product, Order, OrderDetail
from src.api.v1.apps.orders.schemas import FlavorCatalogueCreate, FlavorCatalogueRead, FlavorCatalogueUpdate, OrderDetailReadNested 
from src.api.v1.apps.orders.schemas import MeatCatalogueCreate, MeatCatalogueRead, MeatCatalogueUpdate 
from src.api.v1.apps.orders.schemas import ProductCreate, ProductUpdate
from src.api.v1.apps.orders.schemas import OrderCreate, OrderUpdate, OrderClose, ItemPrepStatus
from src.api.v1.apps.orders.schemas import OrderDetailCreate, OrderDetailUpdateStatus


### --- Orders service class init ---  ####

class OrderService:
    def __init__(self, session: Session):
        """
        Inject the database session so every method operates on the same unit of work.
        """
        self.session = session

    # ==========================================
    # CORE ORDER CRUD METHODS (REFACTORED)
    # ==========================================

    def get_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Retrieve all orders with safe pagination parameters.
        """
        statement = select(Order).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return list(results.all())

    def get_active_orders(self) -> List[Order]:
        """
        Retrieve all active (open) orders.
        """
        statement = select(Order).where(Order.closed == False)
        results = self.session.exec(statement)
        return list(results.all())
    
    def get_order_by_id(self, order_id: int) -> Order:
        """
        Retrieve a specific order database instance. Throws an explicit 404 if missing,
        which gracefully shortcuts to your error middleware.
        """
        order = self.session.get(Order, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found."
            )
        return order

    def create_order(self, user_id: int, order_in: OrderCreate) -> Order:
        """
        Maps the inbound validation schema seamlessly into a database record,
        handles initial nested items safely, calculates totals, and persists.
        """
        # Create base order instance, explicitly injecting the waiter's user_id
        db_order = Order(
            user_id=user_id,
            table_no=order_in.table_no,
            number_of_persons=order_in.number_of_persons,
            created_at=datetime.utcnow()
        )
        
        self.session.add(db_order)
        self.session.flush()  # Flushes to DB to generate db_order.id without committing yet

        # Handle initial items if they were passed inside the open payload
        if order_in.items:
            for item_in in order_in.items:
                db_item = OrderDetail(
                    order_id=db_order.id,
                    person_number=item_in.person_number,
                    product_id=item_in.product_id,
                    flavor_id=item_in.flavor_id,
                    quantity=item_in.quantity,
                    notes=item_in.notes,
                    extra_charge=item_in.extra_charge,
                    prep_status=ItemPrepStatus.QUEUED
                )
                self.session.add(db_item)
        
        # Calculate initial totals dynamically before committing
        self.calculate_order_total(db_order)
        
        self.session.commit()
        self.session.refresh(db_order)
        return db_order

    def update_order(self, order_id: int, order_in: OrderUpdate) -> Order:
        """
        Fetches the target model, maps the payload updates dynamically using 
        Pydantic's update rules, recalculates total financial structures, and persists.
        """
        db_order = self.get_order_by_id(order_id)
        
        if db_order.closed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify attributes on a closed order ledger."
            )

        update_data = order_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
            
        self.calculate_order_total(db_order)
        
        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order)
        return db_order

    def delete_order(self, order_id: int) -> None:
        """
        Locates the targeted item record and deletes it entirely along with cascade sub-items.
        """
        db_order = self.get_order_by_id(order_id)
        self.session.delete(db_order)
        self.session.commit()
        return None

    # ==========================================
    # ORDER ITEM SUB-FLOW WORKFLOWS
    # ==========================================

    def get_all_items_for_order(self, order_id: int) -> List[OrderDetailReadNested]:
        """
        Retrieves all items for a given order, including nested product and flavor details.
        """
        db_order = self.get_order_by_id(order_id)
        if not db_order:
            return []
        return [OrderDetailReadNested.model_validate(item) for item in db_order.items]
    
    def get_all_orders_sended(self) -> List[Order]:
        """
        This method returns all order_id with sended=True
        """
        statement = select(Order).where(
            Order.sended == True,
            Order.closed == False
            ).options(selectinload(Order.items)
            )
        results = self.session.exec(statement)
        return list(results.all())
    
    def get_active_items(self):
        """
        This method uses two internal methods to return active items
        """
        # first: get the orders filter
        orders_filter = self.get_all_orders_sended()
        # now retrieve the items for each order sent
        data = []
        for order in orders_filter:
            individual_order = self.get_all_items_for_order(order.id)
            if len(individual_order) > 0:
                data.extend(individual_order)
        
        return data

    def add_or_update_item(self, order_id: int, item_in: OrderDetailCreate) -> tuple[Order, bool]:
        """
        Adds a product/variant combination to an open ticket. If the product/flavor/seat
        combination already exists, it increments quantity instead.
        Returns a tuple: (Updated Order, boolean indicating if a new row was created).
        """
        db_order = self.get_order_by_id(order_id)
        
        if db_order.closed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add items to a closed and checked-out order."
            )

        statement = select(OrderDetail).where(
            OrderDetail.order_id == order_id,
            OrderDetail.product_id == item_in.product_id,
            OrderDetail.flavor_id == item_in.flavor_id,
            OrderDetail.person_number == item_in.person_number,
            OrderDetail.prep_status == ItemPrepStatus.QUEUED 
        )
        existing_item = self.session.exec(statement).first()

        is_new_item = False  # flag for code response

        if existing_item:
            existing_item.quantity = item_in.quantity
            if item_in.notes:
                existing_item.notes = f"{existing_item.notes} | {item_in.notes}" if existing_item.notes else item_in.notes
            self.session.add(existing_item)
        else:
            db_item = OrderDetail(
                order_id=order_id,
                person_number=item_in.person_number,
                product_id=item_in.product_id,
                flavor_id=item_in.flavor_id,
                selection=item_in.selection,
                quantity=item_in.quantity,
                notes=item_in.notes,
                extra_charge=item_in.extra_charge
            )
            self.session.add(db_item)
            is_new_item = True  # Flag marked as True because a row was added

        self.calculate_order_total(db_order)
        self.session.commit()
        self.session.refresh(db_order)
        
        return db_order, is_new_item

    # first time that the waiter sends an order, the status must change
    def change_sended_status(self, order_id: int) -> bool:
        """
        Safely retrieves the parent Order entity and updates its 'sended' state to True,
        making it visible on the HTMX Live Kitchen Panel.
        """
        # 1. Fetch the correct parent record from the database
        db_order = self.get_order_by_id(order_id)
        if not db_order:
            return False
        
        # 2. Mutate the status column on the parent object directly
        db_order.sended = True
        
        # 3. Commit state changes to the DB session
        try:
            self.session.add(db_order)
            self.session.commit()
            self.session.refresh(db_order)
            return True
        except Exception as e:
            self.session.rollback()
            raise e


    def delete_item(self, order_id: int, item_id: int) -> Order:
        """
        Removes an item row from a ticket. Safety feature: Blocks removal if the item
        is already cooking or delivered to the customer table.
        """
        db_order = self.get_order_by_id(order_id)
        db_item = self.session.get(OrderDetail, item_id)
        
        if not db_item or db_item.order_id != order_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not associated with this order ticket."
            )
            
        if db_item.prep_status != ItemPrepStatus.QUEUED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Lock: Cannot remove an active item that is already being handled by the kitchen staff."
            )

        self.session.delete(db_item)
        self.calculate_order_total(db_order)
        
        self.session.commit()
        self.session.refresh(db_order)
        return db_order

    # ==========================================
    # KITCHEN FLOW & WORKFLOW STATE TRACKERS
    # ==========================================

    def send_to_kitchen(self, order_id: int) -> Order:
        """
        Flips the structural workflow status flag 'sended' to True.
        Makes the command instantly visible on the active chef monitoring console.
        """
        db_order = self.get_order_by_id(order_id)
        if not db_order.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot fire an empty ticket to the kitchen queue."
            )
        
        db_order.sended = True
        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order)
        return db_order

    def update_item_prep_status(self, item_id: int, payload: OrderDetailUpdateStatus) -> OrderDetail:
        """
        Invoked asynchronously by the chef dashboard to shift the prep lifecycle
        state of a single ticket item (QUEUED -> COOKING -> READY). Updates top-level timestamps.
        """
        db_item = self.session.get(OrderDetail, item_id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order item instance {item_id} not found."
            )

        db_item.prep_status = payload.prep_status
        self.session.add(db_item)
        
        # Handle lifecycle timestamp side-effects on parent order if fully delivered
        db_order = db_item.order
        if payload.prep_status == ItemPrepStatus.DELIVERED:
            # Check if every other single item on this ticket is delivered as well
            all_clear = all(item.prep_status == ItemPrepStatus.DELIVERED for item in db_order.items)
            if all_clear:
                db_order.delivered_at = datetime.utcnow()
                self.session.add(db_order)

        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    # ==========================================
    # FINANCIAL COMPUTING ENGINE
    # ==========================================

    def calculate_order_total(self, order: Order) -> None:
        """
        Internal math utility. Sums up all item prices safely utilizing pure Decimal 
        arithmetic, handles modifications/extra charges, applies discounts and tips.
        """
        subtotal = Decimal("0.00")
        
        for item in order.items:
            # Fetch base product price via relationship anchor
            base_price = Decimal(str(item.product.price)) if item.product else Decimal("0.00")
            extra = Decimal(str(item.extra_charge))
            quantity = Decimal(str(item.quantity))
            
            subtotal += (base_price + extra) * quantity
            
        # Total Formula: Subtotal - Discount + Tip
        calculated_total = subtotal - Decimal(str(order.discount)) + Decimal(str(order.tip))
        
        # Safety bound block: prevent billing negative balance errors
        order.total = max(calculated_total, Decimal("0.00"))

    def close_order(self, order_id: int, checkout_payload: OrderClose) -> Order:
        """
        Final system workflow execution. Locks billing totals, attaches tip values,
        registers payment type details, updates timestamps, and sets closed=True.
        """
        db_order = self.get_order_by_id(order_id)
        
        if db_order.closed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket checkout error: This order is already closed and finalized."
            )
            
        if not db_order.sended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot close out a bill that has never been processed or fired to the kitchen."
            )

        # Apply final payment metadata definitions
        db_order.pay_method = checkout_payload.pay_method
        db_order.discount = checkout_payload.discount
        db_order.discount_motive = checkout_payload.discount_motive
        db_order.tip = checkout_payload.tip
        
        # Run final master validation pass on financial formulas
        self.calculate_order_total(db_order)
        
        # Complete system closure sequence operations
        db_order.closed = True
        db_order.closed_at = datetime.now()
        
        self.session.add(db_order)
        self.session.commit()
        self.session.refresh(db_order)
        return db_order



### --- Products service class init ---  ####

class ProductService:
    def __init__(self, session: Session):
        """
        Inject the database session so every method operates on the same unit of work.
        """
        self.session = session

    def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Retrieve all catalogued products with safe pagination parameters.
        """
        statement = select(Product).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Retrieve a specific product. Throws an explicit 404 if missing,
        which gracefully shortcuts to your error middleware.
        """
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )
        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        """
        Maps the inbound validation schema seamlessly into a database record,
        persists it safely, and returns the tracking instance.
        """
        # Convert schema payload to database model entity
        db_product = Product.model_validate(product_in)
        
        self.session.add(db_product)
        self.session.commit()
        self.session.refresh(db_product)
        return db_product

    def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        """
        Fetches the target model, maps the payload updates dynamically using 
        Pydantic's update rules, and persists changes.
        """
        db_product = self.get_product_by_id(product_id)
        
        # Extract the fields sent in the request update data payload
        update_data = product_in.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        self.session.add(db_product)
        self.session.commit()
        self.session.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> None:
        """
        Locates the targeted item record and deletes it entirely.
        """
        db_product = self.get_product_by_id(product_id)
        
        self.session.delete(db_product)
        self.session.commit()
        return None

### Flavors service class init ---

class FlavorService:
    def __init__(self, session: Session):
        """
        Inject the database session so every method operates on the same unit of work.
        """
        self.session = session

    def get_flavors(self, skip: int = 0, limit: int = 100) -> List[FlavorCatalogueRead]:
        """
        Retrieve all catalogued flavors with safe pagination parameters.
        """
        statement = select(FlavorCatalogue).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()

    def get_flavor_by_id(self, flavor_id: int) -> FlavorCatalogue:
        """
        Retrieve a specific flavor. Throws an explicit 404 if missing,
        which gracefully shortcuts to your error middleware.
        """
        flavor = self.session.get(FlavorCatalogue, flavor_id)
        if not flavor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flavor with ID {flavor_id} not found."
            )
        return flavor

    def create_flavor(self, flavor_in: FlavorCatalogueCreate) -> FlavorCatalogue:
        """
        Maps the inbound validation schema seamlessly into a database record,
        persists it safely, and returns the tracking instance.
        """
        # Convert schema payload to database model entity
        db_flavor = FlavorCatalogue.model_validate(flavor_in)
        
        self.session.add(db_flavor)
        self.session.commit()
        self.session.refresh(db_flavor)
        return db_flavor

    def update_flavor(self, flavor_id: int, flavor_in: FlavorCatalogueUpdate) -> FlavorCatalogue:
        """
        Fetches the target model, maps the payload updates dynamically using 
        Pydantic's update rules, and persists changes.
        """
        db_flavor = self.get_flavor_by_id(flavor_id)
        
        # Extract the fields sent in the request update data payload
        update_data = flavor_in.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_flavor, key, value)
            
        self.session.add(db_flavor)
        self.session.commit()
        self.session.refresh(db_flavor)
        return db_flavor

    def delete_flavor(self, flavor_id: int) -> None:
        """
        Locates the targeted item record and deletes it entirely.
        """
        db_flavor = self.get_flavor_by_id(flavor_id)
        
        self.session.delete(db_flavor)
        self.session.commit()
        return None

class MeatService:
    def __init__(self, session: Session):
        """
        Inject the database session so every method operates on the same unit of work.
        """
        self.session = session

    def get_meat_catalogue(self, skip: int = 0, limit: int = 100) -> List[MeatCatalogueRead]:
        """
        Retrieve all catalogued meats with safe pagination parameters.
        """
        try:
            statement = select(MeatCatalogue).offset(skip).limit(limit)
            results = self.session.exec(statement)
            db_meat_list = results.all()
        except Exception as e:
            raise e
        return [MeatCatalogueRead.model_validate(meat) for meat in db_meat_list]

    def get_meat_by_id(self, meat_id: int) -> MeatCatalogue:
        """
        Retrieve a specific meat. Throws an explicit 404 if missing,
        which gracefully shortcuts to your error middleware.
        """
        meat = self.session.get(MeatCatalogue, meat_id)
        if not meat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meat with ID {meat_id} not found."
            )
        return meat

    def create_meat(self, meat_in: MeatCatalogueCreate) -> MeatCatalogue:
        """
        Maps the inbound validation schema seamlessly into a database record,
        persists it safely, and returns the tracking instance.
        """
        # Convert schema payload to database model entity
        db_meat = MeatCatalogue.model_validate(meat_in)
        
        self.session.add(db_meat)
        self.session.commit()
        self.session.refresh(db_meat)
        return db_meat

    def update_meat(self, meat_id: int, meat_in: MeatCatalogueUpdate) -> MeatCatalogue:
        """
        Fetches the target model, maps the payload updates dynamically using 
        Pydantic's update rules, and persists changes.
        """
        db_meat = self.get_meat_by_id(meat_id)
        
        # Extract the fields sent in the request update data payload
        update_data = meat_in.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_meat, key, value)
            
        self.session.add(db_meat)
        self.session.commit()
        self.session.refresh(db_meat)
        return db_meat

    def delete_meat(self, meat_id: int) -> None:
        """
        Locates the targeted item record and deletes it entirely.
        """
        db_meat = self.get_meat_by_id(meat_id)
        
        self.session.delete(db_meat)
        self.session.commit()
        return None