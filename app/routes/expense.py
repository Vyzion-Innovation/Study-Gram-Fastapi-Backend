from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Literal
from fastapi_pagination import Page
import csv
import io

from app.models import User, BasicExpense, SalaryExpense
from app.schemas.expense import *
from app.crud import expense as expense_crud
from app.database.session import get_db
from app.auth.dependencies import get_admin_user

router = APIRouter(prefix="/expenses", tags=["Expense"])


# -------------------- Basic Expense Endpoints --------------------

@router.post("/basic", response_model=BasicExpenseOut)
def create_basic(
        expense: BasicExpenseCreate = Depends(BasicExpenseCreate.as_form),
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.create_basic_expense(db, expense)


@router.get("/basic", response_model=Page[BasicExpenseOut])
def list_basic(
        db: Session = Depends(get_db),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        sort_order: Literal["asc", "desc"] = Query("desc"),
        _: User = Depends(get_admin_user)
):
    return expense_crud.get_basic_expenses(db, start_date, end_date, search, sort_order)


# ✅ Export BEFORE dynamic route to avoid conflict
@router.get("/basic/export")
def export_basic_expenses(
        db: Session = Depends(get_db),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        sort_order: Literal["asc", "desc"] = Query("desc"),
        _: User = Depends(get_admin_user)
):
    query = db.query(BasicExpense)

    if start_date and end_date:
        query = query.filter(BasicExpense.expense_date.between(start_date, end_date))
    if search:
        query = query.filter(BasicExpense.description.ilike(f"%{search}%"))

    query = query.order_by(
        BasicExpense.expense_date.asc() if sort_order == "asc" else BasicExpense.expense_date.desc()
    )

    expenses = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Expense Date", "Amount", "Description", "Created At"])

    for e in expenses:
        writer.writerow([
            e.expense_date.strftime("%Y-%m-%d"),
            e.amount,
            e.expense_date.strftime("%Y-%m-%d") if e.expense_date else "",
            e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=basic_expenses_export.csv"}
    )


@router.get("/basic/{expense_id}", response_model=BasicExpenseOut)
def get_basic_by_id(
        expense_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    expense = db.query(BasicExpense).filter(BasicExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Basic expense not found")
    return expense


@router.put("/basic/{expense_id}", response_model=BasicExpenseOut)
def update_basic(
        expense_id: int,
        data: BasicExpenseUpdate = Depends(BasicExpenseUpdate.as_form),
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.update_basic_expense(db, expense_id, data)


@router.delete("/basic/{expense_id}")
def delete_basic(
        expense_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.delete_basic_expense(db, expense_id)


# -------------------- Salary Expense Endpoints --------------------

@router.post("/salary", response_model=SalaryExpenseOut)
def create_salary(
        expense: SalaryExpenseCreate = Depends(SalaryExpenseCreate.as_form),
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.create_salary_expense(db, expense)


@router.get("/salary", response_model=Page[SalaryExpenseOut])
def list_salary(
        db: Session = Depends(get_db),
        search: Optional[str] = None,
        salary_month: Optional[date] = None,
        sort_order: Literal["asc", "desc"] = Query("desc"),
        _: User = Depends(get_admin_user)
):
    return expense_crud.get_salary_expenses(db, search, salary_month, sort_order)


# ✅ Export BEFORE dynamic route
@router.get("/salary/export")
def export_salary_expenses(
        db: Session = Depends(get_db),
        search: Optional[str] = None,
        salary_month: Optional[date] = None,
        sort_order: Literal["asc", "desc"] = Query("desc"),
        _: User = Depends(get_admin_user)
):
    query = db.query(SalaryExpense).join(SalaryExpense.teacher)

    if salary_month:
        query = query.filter(SalaryExpense.salary_month == salary_month)
    if search:
        query = query.filter(SalaryExpense.description.ilike(f"%{search}%"))

    query = query.order_by(
        SalaryExpense.salary_date.asc() if sort_order == "asc" else SalaryExpense.salary_date.desc()
    )

    expenses = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Teacher Name", "Working Days", "Salary Amount",
        "Salary Month", "Salary Date", "Description", "Created At"
    ])

    for e in expenses:
        writer.writerow([
            e.teacher.name if e.teacher else "",
            e.working_days,
            e.salary_amount,
            e.salary_month.strftime("%Y-%m") if e.salary_month else "",
            e.salary_date.strftime("%Y-%m-%d") if e.salary_date else "",
            e.description,
            e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else ""
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=salary_expenses_export.csv"}
    )

@router.get("/salary/{expense_id}", response_model=SalaryExpenseOut)
def get_salary_by_id(
        expense_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    expense = db.query(SalaryExpense).filter(SalaryExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Salary expense not found")
    return expense


@router.put("/salary/{expense_id}", response_model=SalaryExpenseOut)
def update_salary(
        expense_id: int,
        data: SalaryExpenseUpdate = Depends(SalaryExpenseUpdate.as_form),
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.update_salary_expense(db, expense_id, data)


@router.delete("/salary/{expense_id}")
def delete_salary(
        expense_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_admin_user)
):
    return expense_crud.delete_salary_expense(db, expense_id)
