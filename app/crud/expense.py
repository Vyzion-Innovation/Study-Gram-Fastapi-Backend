from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from fastapi import HTTPException
from app.models import Teacher
from app.models.expense import BasicExpense, SalaryExpense
from app.schemas.expense import BasicExpenseCreate, SalaryExpenseCreate, BasicExpenseUpdate, SalaryExpenseUpdate
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional
# Create functions
def create_basic_expense(db: Session, expense: BasicExpenseCreate):
    obj = BasicExpense(**expense.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def create_salary_expense(db: Session, expense: SalaryExpenseCreate):
    obj = SalaryExpense(**expense.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# Get functions with filters
def get_basic_expenses(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    sort_order: str = "desc"
):
    query = db.query(BasicExpense)

    if start_date and end_date:
        query = query.filter(BasicExpense.expense_date.between(start_date, end_date))
    if search:
        query = query.filter(BasicExpense.description.ilike(f"%{search}%"))

    # Sorting logic
    if sort_order == "asc":
        query = query.order_by(BasicExpense.created_at.asc())
    else:
        query = query.order_by(BasicExpense.created_at.desc())

    return paginate(query)

def get_salary_expenses(
    db: Session,
    search: Optional[str] = None,
    salary_month: Optional[date] = None,
    sort_order: str = "desc"
):
    query = db.query(SalaryExpense).join(SalaryExpense.teacher)

    # Filter by teacher name
    if search:
        query = query.filter(Teacher.name.ilike(f"%{search}%"))

    # Filter by salary month using date range
    if salary_month:
        start_date = salary_month.replace(day=1)
    else:
        start_date = date.today().replace(day=1)

    if start_date.month == 12:
        next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
    else:
        next_month = start_date.replace(month=start_date.month + 1, day=1)

    end_date = next_month - timedelta(days=1)

    query = query.filter(SalaryExpense.salary_month.between(start_date, end_date))

    # Sorting
    if sort_order == "asc":
        query = query.order_by(SalaryExpense.created_at.asc())
    else:
        query = query.order_by(SalaryExpense.created_at.desc())

    return paginate(query)


# Update Basic Expense
def update_basic_expense(db: Session, expense_id: int, data: BasicExpenseUpdate):
    obj = db.query(BasicExpense).filter(BasicExpense.id == expense_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Basic expense not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

# Delete Basic Expense
def delete_basic_expense(db: Session, expense_id: int):
    obj = db.query(BasicExpense).filter(BasicExpense.id == expense_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Basic expense not found")
    db.delete(obj)
    db.commit()
    return {"message": "Basic expense deleted successfully"}

# Update Salary Expense
def update_salary_expense(db: Session, expense_id: int, data: SalaryExpenseUpdate):
    obj = db.query(SalaryExpense).filter(SalaryExpense.id == expense_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary expense not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

# Delete Salary Expense
def delete_salary_expense(db: Session, expense_id: int):
    obj = db.query(SalaryExpense).filter(SalaryExpense.id == expense_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary expense not found")
    db.delete(obj)
    db.commit()
    return {"message": "Salary expense deleted successfully"}

# Total for current month
def get_total_expense_this_month(db: Session):
    today = datetime.today()

    # Start of current month
    month_start = today.replace(day=1)

    # Start of next month
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1, day=1)

    query1 = db.query(func.sum(BasicExpense.amount)).filter(
        BasicExpense.expense_date >= month_start,
        BasicExpense.expense_date < month_end
    )

    query2 = db.query(func.sum(SalaryExpense.salary_amount)).filter(
        SalaryExpense.salary_date >= month_start,
        SalaryExpense.salary_date < month_end
    )

    total_basic = query1.scalar() or 0
    total_salary = query2.scalar() or 0

    return {
        "total_basic_expense": total_basic,
        "total_salary_expense": total_salary,
        "total_expense": total_basic + total_salary
    }