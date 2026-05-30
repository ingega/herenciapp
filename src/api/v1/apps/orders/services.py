# src/api/v1/apps/orders/services.py

from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.api.v1.apps.orders.models import Product
from src.api.v1.apps.orders.schemas import ProductCreate, ProductBase, ProductUpdate


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
    