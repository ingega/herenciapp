# src/api/v1/apps/expenses/router.py
from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.database import get_session
from src.api.v1.apps.expenses.models import ExpensesCategory
from src.api.v1.apps.expenses.schemas import ExpenseBatchCreate, ExpenseCreate, ExpenseRead, ExpenseUpdate
from src.api.v1.apps.expenses.services import ExpenseService
from src.api.v1.auth.auth import get_current_user_from_cookie
from src.config import settings
from src.__init__ import __version__ as version

router = APIRouter(prefix="/expenses", tags=["expenses"], redirect_slashes=False)

# Jinja templates for this router
templates = Jinja2Templates(directory="src/templates")


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


@router.post("/batch", response_model=List[ExpenseRead], status_code=status.HTTP_201_CREATED)
def create_expenses_batch(payload: ExpenseBatchCreate, service: ExpenseService = Depends(get_expense_service)):
    """Create several expenses in one atomic transaction."""
    created = service.add_expenses_batch(payload.items)
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create expenses batch")
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


@router.get('/add/add_expenses', response_class=HTMLResponse, 
            status_code=status.HTTP_200_OK)
def add_expenses_view(request: Request, 
                      current_user: dict = Depends(get_current_user_from_cookie),
                      session: Session = Depends(get_session)):
    """Render the expenses template allowing the user to add/edit/delete multiple expense rows.

    Returns a 201 Created response with the rendered HTML for consistency with the UI flow.
    """
    # metadata to help the template (categories, app version, config, current user)
    categories = session.exec(
        select(ExpensesCategory)
        .where(ExpensesCategory.active == True)
        .order_by(ExpensesCategory.name)
    ).all()
    return templates.TemplateResponse(
        name='expenses/expenses.html',
        request=request,
        context={
            'config': settings,
            'current_user': current_user,
            'version': version,
            'categories': [category.name for category in categories],
        },
        status_code=status.HTTP_201_CREATED
    )
