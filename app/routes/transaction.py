import csv
from enum import Enum
from io import StringIO
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from starlette.responses import StreamingResponse
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.transaction import Transaction
from app.models.regular_student import RegularStudent
from app.schemas.transaction import TransactionCreate, TransactionOut

from datetime import datetime, date, timedelta

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/transactions", response_model=TransactionOut)
def create_transaction(data: TransactionCreate = Depends(TransactionCreate.as_form), db: Session = Depends(get_db)):


    student = db.query(RegularStudent).filter(RegularStudent.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    monthly_fee = student.batch_fee_per_month

    # Get latest transaction for student
    last_txn = (
        db.query(Transaction)
        .filter(Transaction.student_id == student.id)
        .order_by(Transaction.payment_month_end.desc())
        .first()
    )

    if not last_txn:
        # First month payment
        start_date = student.admission_date
        end_date = start_date + timedelta(days=30)
        already_paid = 0
    else:
        # Check if previous month is fully paid
        previous_total = db.query(func.sum(Transaction.amount_paid)).filter(
            Transaction.student_id == student.id,
            Transaction.payment_month_start == last_txn.payment_month_start,
            Transaction.payment_month_end == last_txn.payment_month_end,
        ).scalar() or 0

        if previous_total < monthly_fee:
            # Still has pending for current month
            start_date = last_txn.payment_month_start
            end_date = last_txn.payment_month_end
            already_paid = previous_total
        else:
            # Go to next month
            start_date = last_txn.payment_month_end
            end_date = start_date + timedelta(days=30)
            already_paid = 0

    if already_paid + data.amount_paid > monthly_fee:
        raise HTTPException(
            status_code=400,
            detail=f"Payment exceeds monthly fee. Already paid: {already_paid}, Trying to pay: {data.amount_paid}, Fee: {monthly_fee}"
        )

    # ✅ Fixed: Include missing fields
    txn = Transaction(
        student_id=student.id,
        amount_paid=data.amount_paid,
        payment_month_start=start_date,
        payment_month_end=end_date,
        payment_date=data.payment_date,
        pending_amount=monthly_fee - (already_paid + data.amount_paid),  # ✅ Add pending_amount
        payment_method=data.payment_method,  # ✅ Add payment_method
        created_at=datetime.utcnow()
    )

    db.add(txn)
    db.commit()
    db.refresh(txn)

    return txn


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/", response_model=Page[TransactionOut])
def list_transactions(
    payment_month: Optional[date] = Query(default_factory=lambda: datetime.now().date()),
    sort_order: SortOrder = Query(default=SortOrder.desc, description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Step 1: Get the start and end of the month
    month_start = payment_month.replace(day=1)

    # First day of next month
    if month_start.month == 12:
        next_month_start = month_start.replace(year=month_start.year + 1, month=1, day=1)
    else:
        next_month_start = month_start.replace(month=month_start.month + 1, day=1)

    # Step 2: Filter where payment_month_start falls within the month
    query = db.query(Transaction).filter(
        Transaction.payment_month_start >= month_start,
        Transaction.payment_month_start < next_month_start
    )

    # Step 3: Apply sort
    if sort_order == SortOrder.asc:
        query = query.order_by(Transaction.created_at.asc())
    else:
        query = query.order_by(Transaction.created_at.desc())

    return sqlalchemy_paginate(query)


@router.get("/export")
def export_transactions(
    payment_month: Optional[date] = Query(default=None, description="Filter by payment month"),
    sort_order: SortOrder = Query(default=SortOrder.desc, description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Transaction).join(Transaction.student)

    if payment_month:
        start_date = payment_month.replace(day=1)
        if start_date.month == 12:
            next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            next_month = start_date.replace(month=start_date.month + 1, day=1)

        # Filter by payment_month_start
        query = query.filter(
            Transaction.payment_month_start >= start_date,
            Transaction.payment_month_start < next_month
        )

    if sort_order == SortOrder.asc:
        query = query.order_by(Transaction.created_at.asc())
    else:
        query = query.order_by(Transaction.created_at.desc())

    transactions = query.all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student Name",
        "Payment Date",
        "Payment Month",
        "Amount Paid",
        "Pending Amount",
        "Payment Method",
        "Created At"
    ])

    for t in transactions:
        writer.writerow([
            t.student.name if t.student else "Unknown",
            t.payment_date.strftime("%Y-%m-%d") if t.payment_date else "",
            t.payment_month_start.strftime("%Y-%m") if t.payment_month_start else "",
            t.amount_paid,
            t.pending_amount,
            t.payment_method,
            t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )


@router.get("/monthly-earning")
def get_total_earning(
    payment_month: Optional[date] = Query(default_factory=lambda: datetime.today().date()),
    db: Session = Depends(get_db)
):
    try:
        # Get the first day of the provided month
        start_date = payment_month.replace(day=1)

        # Get the first day of the next month
        if start_date.month == 12:
            next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            next_month = start_date.replace(month=start_date.month + 1, day=1)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get total earnings for the month (between first and last day)
    total = db.query(func.coalesce(func.sum(Transaction.amount_paid), 0)).filter(
        Transaction.payment_month_start >= start_date,
        Transaction.payment_month_start < next_month
    ).scalar()

    return {
        "month": start_date.strftime("%Y-%m"),
        "total_earning": total
    }
