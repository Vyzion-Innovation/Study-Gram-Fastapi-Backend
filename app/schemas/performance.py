from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum
from fastapi import Form

class StudentTypeEnum(str, Enum):
    new_student = "new_student"
    existing_student = "existing_student"

class PerformanceBase(BaseModel):
    student_type: StudentTypeEnum
    select_student: Optional[int] = None  # ForeignKey to regular_students
    name: str
    admission_number: str
    test_date: date
    speaking: Optional[str] = None
    writing: Optional[str] = None
    listening: Optional[str] = None
    reading: Optional[str] = None
    overall: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        student_type: StudentTypeEnum = Form(...),
        select_student: Optional[str] = Form(None),
        name: str = Form(...),
        admission_number: str = Form(...),
        test_date: date = Form(...),
        speaking: Optional[str] = Form(None),
        writing: Optional[str] = Form(None),
        listening: Optional[str] = Form(None),
        reading: Optional[str] = Form(None),
        overall: Optional[str] = Form(None),
    ):
        # Convert select_student from string to int if not empty
        try:
            select_student_int = int(select_student) if select_student not in (None, "", "null") else None
        except ValueError:
            select_student_int = None

        return cls(
            student_type=student_type,
            select_student=select_student_int,  # ✅ fixed field name here
            name=name,
            admission_number=admission_number,
            test_date=test_date,
            speaking=speaking,
            writing=writing,
            listening=listening,
            reading=reading,
            overall=overall,
        )

class PerformanceCreate(PerformanceBase):
    pass

class PerformanceUpdate(BaseModel):
    student_type: Optional[StudentTypeEnum] = None
    select_student: Optional[int] = None
    name: Optional[str] = None
    admission_number: Optional[str] = None
    test_date: Optional[date] = None
    speaking: Optional[str] = None
    writing: Optional[str] = None
    listening: Optional[str] = None
    reading: Optional[str] = None
    overall: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        student_type: Optional[StudentTypeEnum] = Form(None),
        select_student: Optional[str] = Form(None),
        name: Optional[str] = Form(None),
        admission_number: Optional[str] = Form(None),
        test_date: Optional[date] = Form(None),
        speaking: Optional[str] = Form(None),
        writing: Optional[str] = Form(None),
        listening: Optional[str] = Form(None),
        reading: Optional[str] = Form(None),
        overall: Optional[str] = Form(None),
    ):
        try:
            select_student_int = int(select_student) if select_student not in (None, "", "null") else None
        except ValueError:
            select_student_int = None

        return cls(
            student_type=student_type,
            select_student=select_student_int,
            name=name,
            admission_number=admission_number,
            test_date=test_date,
            speaking=speaking,
            writing=writing,
            listening=listening,
            reading=reading,
            overall=overall,
        )

class PerformanceOut(PerformanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
