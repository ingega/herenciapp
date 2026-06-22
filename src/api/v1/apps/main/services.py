# src/api/v1/apps/main/services.py
from fastapi import Depends
from src.api.v1.apps.orders.models import Order
from sqlmodel import Session, select, func
from datetime import date, timedelta

class FinancialService:
    """
    This class retrieves functions and queriues for dashboard and financial reports
    """
    def __init__(self, session: Session):
        """Use the common session for all methods"""
        self.session = session
    
    def get_totals_per_date(self, initial_date: date, final_date: date) -> dict:
        """
        This method retrieves the total ammount for
        - Orders
        - Discounts
        - Tips
        :params:
            initial_date: datetime. Statistics initial date
            final_date: datetime. Statistics final date
        """
        # defensive code
        try:
            # closed_at is datetime, let's get 1 more day
            bod = initial_date  # begining of date
            eod = final_date + timedelta(1) # end of date plus one
            statement = select(
                func.coalesce(func.sum(Order.total), 0).label("sales"),
                func.coalesce(func.sum(Order.discount), 0).label("discount"),
                func.coalesce(func.sum(Order.tip), 0).label("tips"),
                func.count(Order.id).label("orders")
            ).where(
                Order.closed_at >= bod,
                Order.closed_at < eod
            )
            
            # Exec devuelve una tupla con los alias definidos en los labels
            row = self.session.exec(statement).first()
            # retrieve data, initial dict with zero
            return {"sales": row.sales, 
                    "discount": row.discount, 
                    "tips": row.tips, 
                    "orders": row.orders,
                    "avg_ticket": (row.sales / row.orders) if row.orders > 0 else 0,
                    "initial_date": initial_date,
                    "final_date": final_date
                    }
            
        except Exception as e:
            raise e
               

