from pydantic import BaseModel
from datetime import date
from typing import Optional
from fastapi import Form

# ---------- BasicExpense ----------

class BasicExpenseCreate(BaseModel):
    expense_date: date
    amount: float
    description: str

    @classmethod
    def as_form(
        cls,
        expense_date: date = Form(...),
        amount: float = Form(...),
        description: str = Form(...),
    ):
        return cls(
            expense_date=expense_date,
            amount=amount,
            description=description,
        )

class BasicExpenseUpdate(BaseModel):
    expense_date: Optional[date]
    amount: Optional[float]
    description: Optional[str]

    @classmethod
    def as_form(
        cls,
        expense_date: Optional[date] = Form(None),
        amount: Optional[float] = Form(None),
        description: Optional[str] = Form(None),
    ):
        return cls(
            expense_date=expense_date,
            amount=amount,
            description=description,
        )

class BasicExpenseOut(BasicExpenseCreate):
    id: int

    class Config:
        orm_mode = True


# ---------- SalaryExpense ----------

class SalaryExpenseCreate(BaseModel):
    teacher_id: int
    working_days: int
    salary_amount: float
    salary_month: date  # Changed from str to date
    salary_date: date
    description: str

    @classmethod
    def as_form(
        cls,
        teacher_id: int = Form(...),
        working_days: int = Form(...),
        salary_amount: float = Form(...),
        salary_month: date = Form(...),  # Updated type
        salary_date: date = Form(...),
        description: str = Form(...),
    ):
        return cls(
            teacher_id=teacher_id,
            working_days=working_days,
            salary_amount=salary_amount,
            salary_month=salary_month,
            salary_date=salary_date,
            description=description,
        )

class SalaryExpenseUpdate(BaseModel):
    teacher_id: Optional[int]
    working_days: Optional[int]
    salary_amount: Optional[float]
    salary_month: Optional[date]  # Changed from str to date
    salary_date: Optional[date]
    description: Optional[str]

    @classmethod
    def as_form(
        cls,
        teacher_id: Optional[int] = Form(None),
        working_days: Optional[int] = Form(None),
        salary_amount: Optional[float] = Form(None),
        salary_month: Optional[date] = Form(None),  # Updated type
        salary_date: Optional[date] = Form(None),
        description: Optional[str] = Form(None),
    ):
        return cls(
            teacher_id=teacher_id,
            working_days=working_days,
            salary_amount=salary_amount,
            salary_month=salary_month,
            salary_date=salary_date,
            description=description,
        )

class SalaryExpenseOut(SalaryExpenseCreate):
    id: int

    class Config:
        orm_mode = True
