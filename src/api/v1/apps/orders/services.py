# src/api/v1/apps/orders/services.py

from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.api.v1.apps.orders.models import FlavorCatalogue, MeatCatalogue, Product
from src.api.v1.apps.orders.schemas import FlavorCatalogueCreate, FlavorCatalogueRead, FlavorCatalogueUpdate, MeatCatalogueCreate, MeatCatalogueRead, ProductCreate, ProductBase, ProductUpdate


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
        statement = select(MeatCatalogue).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()

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