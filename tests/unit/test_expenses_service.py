from datetime import datetime, timedelta
from sqlmodel import Session

from src.api.v1.apps.expenses.services import ExpenseService
from src.api.v1.apps.expenses.models import Expenses, ExpensesCategory
from src.api.v1.apps.expenses.schemas import ExpenseCreate, ExpenseUpdate


def make_expense(date: datetime, expense: str = "Item", category: str = "beverages", quantity: float = 1.0, total: float = 10.0) -> Expenses:
    return Expenses(date=date, expense=expense, category=category, quantity=quantity, total=total)


def test_expense_service_crud(session: Session):
    service = ExpenseService(session)

    # initially empty
    today = datetime.utcnow()
    assert service.get_expenses_by_date(today.date()) == []

    # add expense
    payload = ExpenseCreate(expense="Coffee", total=2.5, category="bebidas")
    created = service.add_expense(payload)
    assert created is not None
    assert created.id is not None
    assert created.expense == "Coffee"

    # get by id
    fetched = service.get_expenses_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id

    # update expense
    update = ExpenseUpdate(total=3.0)
    updated = service.update_expense(created.id, update)
    assert updated is not None
    assert updated.total == 3.0

    # range query
    start = (today - timedelta(days=1)).date()
    end = (today + timedelta(days=1)).date()
    results = service.get_expenses_by_date_range(start, end)
    assert isinstance(results, list)
    assert any(r.id == created.id for r in results)

    # delete
    ok = service.delete_expense_by_id(created.id)
    assert ok is True
    assert service.get_expenses_by_id(created.id) is None
