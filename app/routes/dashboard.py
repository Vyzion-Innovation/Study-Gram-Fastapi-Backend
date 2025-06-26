
from tokenize import String
from sqlalchemy import func, and_, asc, desc, cast, String, text, extract
from app.models import Batch, Teacher, User, Transaction, BasicExpense, SalaryExpense
from typing import List, Optional, Literal
from datetime import date, datetime, timedelta
from app.crud import expense as expense_crud
from app.models.regular_student import RegularStudent
from app.schemas.dashboard import PendingFeeStudentOut
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user

from sqlalchemy.orm import aliased

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/current-month-pending")
def get_current_month_students_with_no_or_partial_payment(
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by admission_date"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    today = datetime.today()
    month_start = today.replace(day=1).date()
    month_end = (today.replace(day=1) + timedelta(days=32)).replace(day=1).date()

    # Step 1: Fetch students admitted this month
    students = db.query(RegularStudent).filter(
        RegularStudent.admission_date >= month_start,
        RegularStudent.admission_date < month_end
    ).order_by(
        RegularStudent.admission_date.asc() if sort_order == "asc" else RegularStudent.admission_date.desc()
    ).all()

    result = []
    for student in students:
        # Get total paid for this month
        total_paid = db.query(func.sum(Transaction.amount_paid)).filter(
            Transaction.student_id == student.id,
            func.date(Transaction.payment_month_start) >= month_start,
            func.date(Transaction.payment_month_start) < month_end
        ).scalar() or 0

        if total_paid < student.batch_fee_per_month:
            result.append({
                "student_name": student.name,
                "admission_date": student.admission_date,
                "pending_amount": float(student.batch_fee_per_month - total_paid),
            })

    return {"data": result}


@router.get("/count")
def get_table_count(
        table_name: str = Query(..., description="Name of the table: regular_student, batch, teacher"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    # Mapping table name to model
    table_map = {
        "regular_student": RegularStudent,
        "batch": Batch,
        "teacher": Teacher,
    }

    model = table_map.get(table_name.lower())
    if not model:
        raise HTTPException(status_code=400, detail="Invalid table name")

    # Apply filter conditionally
    if table_name.lower() in ["regular_student", "teacher"]:
        count = db.query(model).filter(model.status == "active").count()
    else:
        count = db.query(model).count()

    return {"table": table_name, "count": count}


@router.get("/total-monthly-expense")
def total_monthly(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return expense_crud.get_total_expense_this_month(db)

@router.get("/pending-current-month-fees", response_model=Page[PendingFeeStudentOut])
def get_students_with_pending_fees(
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by admission_date"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    today = datetime.today().date()
    first_day_current_month = today.replace(day=1)

    # Next month for upper bound filter
    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    # Subquery: total paid by each student for current month
    subquery = (
        db.query(
            Transaction.student_id.label("student_id"),
            func.sum(Transaction.amount_paid).label("total_paid")
        )
        .filter(
            Transaction.payment_month_start >= first_day_current_month,
            Transaction.payment_month_start < next_month
        )
        .group_by(Transaction.student_id)
        .subquery()
    )

    Subq = aliased(subquery)

    # Due date logic: set as the admission day but in current month
    due_date_expr = func.to_date(
        func.concat(
            func.to_char(func.current_date(), 'YYYY-MM-'),
            func.lpad(cast(func.extract('day', RegularStudent.admission_date), String), 2, '0')
        ),
        text("'YYYY-MM-DD'")
    )

    query = (
        db.query(
            RegularStudent.name.label("student_name"),
            RegularStudent.admission_date,
            (
                RegularStudent.batch_fee_per_month - func.coalesce(Subq.c.total_paid, 0)
            ).label("pending_amount"),
            due_date_expr.label("due_date")
        )
        .outerjoin(Subq, RegularStudent.id == Subq.c.student_id)
        .filter(
            and_(
                func.coalesce(Subq.c.total_paid, 0) < RegularStudent.batch_fee_per_month,
                RegularStudent.admission_date < first_day_current_month
            )
        )
        .order_by(
            asc(RegularStudent.admission_date) if sort_order == "asc" else desc(RegularStudent.admission_date)
        )
    )

    return sqlalchemy_paginate(query)

@router.get("/pending-last-month-fees", response_model=Page[PendingFeeStudentOut])
def get_students_with_pending_fees_last_month(
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by admission_date"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    today = datetime.today().date()

    # Get first day of current and last month
    first_day_current_month = today.replace(day=1)
    if first_day_current_month.month == 1:
        first_day_last_month = date(first_day_current_month.year - 1, 12, 1)
    else:
        first_day_last_month = date(first_day_current_month.year, first_day_current_month.month - 1, 1)

    # Get first day of the month after last month
    if first_day_last_month.month == 12:
        first_day_next_of_last_month = date(first_day_last_month.year + 1, 1, 1)
    else:
        first_day_next_of_last_month = date(first_day_last_month.year, first_day_last_month.month + 1, 1)

    # Subquery: Total paid per student for last month
    subquery = (
        db.query(
            Transaction.student_id.label("student_id"),
            func.sum(Transaction.amount_paid).label("total_paid")
        )
        .filter(
            Transaction.payment_month_start >= first_day_last_month,
            Transaction.payment_month_start < first_day_next_of_last_month
        )
        .group_by(Transaction.student_id)
        .subquery()
    )

    Subq = aliased(subquery)

    # Due date logic: last month's due date = same day as admission but in last month
    due_date_expr = func.to_date(
        func.concat(
            func.to_char(first_day_current_month, 'YYYY-MM-'),
            func.lpad(cast(func.extract('day', RegularStudent.admission_date), String), 2, '0')
        ),
        text("'YYYY-MM-DD'")
    )

    query = (
        db.query(
            RegularStudent.name.label("student_name"),
            RegularStudent.admission_date,
            (
                RegularStudent.batch_fee_per_month - func.coalesce(Subq.c.total_paid, 0)
            ).label("pending_amount"),
            due_date_expr.label("due_date")
        )
        .outerjoin(Subq, RegularStudent.id == Subq.c.student_id)
        .filter(
            and_(
                RegularStudent.admission_date < first_day_current_month,  # Exclude current month students
                func.coalesce(Subq.c.total_paid, 0) < RegularStudent.batch_fee_per_month
            )
        )
        .order_by(
            asc(RegularStudent.admission_date) if sort_order == "asc" else desc(RegularStudent.admission_date)
        )
    )

    return sqlalchemy_paginate(query)


#
# @router.get("/monthly-profit")
# def get_monthly_profit_data(db: Session = Depends(get_db)):
#     try:
#         today = datetime.today()
#         results = []
#
#         for i in range(6):
#             # Calculate the first and last date of the month
#             target_month = today.replace(day=1) - timedelta(days=30 * i)
#             year = target_month.year
#             month = target_month.month
#
#             # === INCOME ===
#             income = db.query(func.coalesce(func.sum(Transaction.amount_paid), 0))\
#                 .filter(
#                     extract('year', Transaction.payment_date) == year,
#                     extract('month', Transaction.payment_date) == month
#                 ).scalar()
#
#             # === BASIC EXPENSES ===
#             basic_expense = db.query(func.coalesce(func.sum(BasicExpense.amount), 0))\
#                 .filter(
#                     extract('year', BasicExpense.expense_date) == year,
#                     extract('month', BasicExpense.expense_date) == month
#                 ).scalar()
#
#             # === SALARY EXPENSES ===
#             salary_expense = db.query(func.coalesce(func.sum(SalaryExpense.salary_amount), 0))\
#                 .filter(
#                     extract('year', SalaryExpense.salary_date) == year,
#                     extract('month', SalaryExpense.salary_date) == month
#                 ).scalar()
#
#             total_expense = basic_expense + salary_expense
#             profit = income - total_expense
#
#             results.append({
#                 "month": target_month.strftime("%B %Y"),
#                 "income": income,
#                 "expense": total_expense,
#                 "profit": profit
#             })
#
#         # Reverse to show from oldest to latest
#         results.reverse()
#
#         return {"data": results}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")