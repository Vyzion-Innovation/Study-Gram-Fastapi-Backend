from pydantic import BaseModel
from fastapi import Form
from typing import Literal, Optional
from datetime import date, datetime

class TransactionCreate(BaseModel):
    student_id: int
    payment_date: date
    amount_paid: float
    payment_method: Literal["cash", "card", "upi"]

    @classmethod
    def as_form(
        cls,
        student_id: int = Form(...),
        payment_date: date = Form(...),
        amount_paid: float = Form(...),
        payment_method: Literal["cash", "card", "upi"] = Form(...),
    ):
        return cls(
            student_id=student_id,
            payment_date=payment_date,
            amount_paid=amount_paid,
            payment_method=payment_method,
        )


class TransactionOut(BaseModel):
    id: int
    student_id: int
    payment_date: date
    payment_month_start: date
    payment_month_end: date
    amount_paid: float
    pending_amount: float
    payment_method: str
    created_at: datetime

    class Config:
        orm_mode = True
