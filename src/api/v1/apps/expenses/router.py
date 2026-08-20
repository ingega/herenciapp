# src/api/v1/apps/expenses/router.py
from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_session
from src.api.v1.apps.expenses.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
from src.api.v1.apps.expenses.services import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"], redirect_slashes=False)


def get_expense_service(session: Session = Depends(get_session)) -> ExpenseService:
    return ExpenseService(session)


@router.get("/", response_model=List[ExpenseRead])
def list_expenses_by_date(date: date, service: ExpenseService = Depends(get_expense_service)):
    """List expenses for a specific date (YYYY-MM-DD)."""
    results = service.get_expenses_by_date(date)
    return results


@router.get("/range", response_model=List[ExpenseRead])
def list_expenses_by_range(start: date, end: date, service: ExpenseService = Depends(get_expense_service)):
    """List expenses within an inclusive date range (start..end)."""
    results = service.get_expenses_by_date_range(start, end)
    return results


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, service: ExpenseService = Depends(get_expense_service)):
    """Retrieve a single expense by id."""
    expense = service.get_expenses_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.post("/", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, service: ExpenseService = Depends(get_expense_service)):
    """Create a new expense."""
    created = service.add_expense(payload)
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create expense")
    return created


@router.patch("/{expense_id}", response_model=ExpenseRead)
def patch_expense(expense_id: int, payload: ExpenseUpdate, service: ExpenseService = Depends(get_expense_service)):
    """Partially update an expense."""
    updated = service.update_expense(expense_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found or not updated")
    return updated


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, service: ExpenseService = Depends(get_expense_service)):
    """Delete expense by id."""
    ok = service.delete_expense_by_id(expense_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return None
