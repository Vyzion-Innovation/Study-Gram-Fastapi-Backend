from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum
from fastapi import Form

class StudentTypeEnum(str, Enum):
    new_student = "new_student"
    existing_student = "existing_student"

class MockTestBase(BaseModel):
    student_type: StudentTypeEnum
    select_student: Optional[int] = None
    name: str
    admission_number: str
    test_date: date
    speaking: str
    writing: str
    listening: str
    reading: str
    overall: str

    @classmethod
    def as_form(
        cls,
        student_type: StudentTypeEnum = Form(...),
        select_student: Optional[int] = Form(None),
        name: str = Form(...),
        admission_number: str = Form(...),
        test_date: date = Form(...),
        speaking: str = Form(...),
        writing: str = Form(...),
        listening: str = Form(...),
        reading: str = Form(...),
        overall: str = Form(...),
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

class MockTestCreate(MockTestBase):
    pass

class MockTestUpdate(BaseModel):
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
        select_student: Optional[int] = Form(None),
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

class MockTestOut(MockTestBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
