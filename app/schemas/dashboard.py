# app/schemas/student.py (create if needed)
from pydantic import BaseModel
from datetime import date

class PendingFeeStudentOut(BaseModel):
    student_name: str
    admission_date: date
    pending_amount: float
    due_date: date

    class Config:
        orm_mode = True
