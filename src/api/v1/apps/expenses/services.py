# src/api/v1/apps/expenses/services.py
from datetime import date, datetime, timedelta
import logging
from typing import Optional, List

from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError

from src.api.v1.apps.expenses.models import Expenses
from src.api.v1.apps.expenses.schemas import ExpenseCreate, ExpenseUpdate

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service class that provides CRUD operations for Expenses."""

    def __init__(self, session: Session):
        self.session = session

    def get_expenses_by_date(self, target_date: date) -> List[Expenses]:
        """Return all expenses for a given date (UTC-aware, matches whole day)."""
        try:
            bod = datetime(target_date.year, target_date.month, target_date.day)
            eod = bod + timedelta(days=1)
            statement = select(Expenses).where(Expenses.date >= bod, Expenses.date < eod)
            results = self.session.exec(statement).all()
            return results
        except SQLAlchemyError as e:
            logger.error(f"DB error fetching expenses by date {target_date}: {e}")
            return []

    def get_expenses_by_id(self, expense_id: int) -> Optional[Expenses]:
        """Return a single expense by primary key or None if not found."""
        try:
            expense = self.session.get(Expenses, expense_id)
            if not expense:
                logger.info(f"Expense not found for id: {expense_id}")
            return expense
        except SQLAlchemyError as e:
            logger.error(f"DB error fetching expense by id {expense_id}: {e}")
            return None

    def get_expenses_by_date_range(self, start_date: date, end_date: date) -> List[Expenses]:
        """Return expenses within an inclusive date range (start_date..end_date)."""
        try:
            bod = datetime(start_date.year, start_date.month, start_date.day)
            eod = datetime(end_date.year, end_date.month, end_date.day) + timedelta(days=1)
            statement = select(Expenses).where(Expenses.date >= bod, Expenses.date < eod)
            results = self.session.exec(statement).all()
            return results
        except SQLAlchemyError as e:
            logger.error(f"DB error fetching expenses range {start_date} - {end_date}: {e}")
            return []

    def add_expense(self, expense_in: ExpenseCreate) -> Optional[Expenses]:
        """Create and persist a new Expenses row. Returns the created Expenses or None on failure."""
        try:
            payload = expense_in.dict()
            new_expense = Expenses(**payload)
            self.session.add(new_expense)
            self.session.commit()
            self.session.refresh(new_expense)
            return new_expense
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to add expense: {e}")
            return None

    def update_expense(self, expense_id: int, data: ExpenseUpdate) -> Optional[Expenses]:
        """Update an existing expense with partial data. Returns updated Expenses or None."""
        try:
            expense = self.session.get(Expenses, expense_id)
            if not expense:
                return None

            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(expense, key, value)

            self.session.add(expense)
            self.session.commit()
            self.session.refresh(expense)
            return expense
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update expense {expense_id}: {e}")
            return None

    def delete_expense_by_id(self, expense_id: int) -> bool:
        """Delete expense by id. Returns True if deleted, False otherwise."""
        try:
            expense = self.session.get(Expenses, expense_id)
            if not expense:
                return False
            self.session.delete(expense)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete expense {expense_id}: {e}")
            return False
