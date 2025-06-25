# app/schemas/pte_student.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from fastapi import Form
from enum import Enum


class StudentTypeEnum(str, Enum):
    new_student = "new_student"
    existing_student = "existing_student"


class LowercaseMixin:
    def __init__(self, **data):
        for field in self.__annotations__:
            value = data.get(field)
            if isinstance(value, str):
                data[field] = value.lower()
        super().__init__(**data)


class PTEStudentBase(BaseModel, LowercaseMixin):
    student_type: StudentTypeEnum
    select_student: Optional[int] = None
    pte_id: str
    pte_username: str
    pte_vouchername: str
    pte_password: str
    email: EmailStr
    contact_number: str

    @classmethod
    def as_form(
        cls,
        student_type: StudentTypeEnum = Form(...),
        select_student: Optional[int] = Form(None),
        pte_id: str = Form(...),
        pte_username: str = Form(...),
        pte_vouchername: str = Form(...),
        pte_password: str = Form(...),
        email: EmailStr = Form(...),
        contact_number: str = Form(...),
    ):
        try:
            select_student_int = int(select_student) if select_student not in (None, "", "null") else None
        except ValueError:
            select_student_int = None

        return cls(
            student_type=student_type,
            select_student=select_student_int,
            pte_id=pte_id,
            pte_username=pte_username,
            pte_vouchername=pte_vouchername,
            pte_password=pte_password,
            email=email,
            contact_number=contact_number,
        )


class PTEStudentCreate(PTEStudentBase):
    pass


class PTEStudentUpdate(BaseModel, LowercaseMixin):
    student_type: Optional[StudentTypeEnum] = None
    select_student: Optional[int] = None
    pte_id: Optional[str] = None
    pte_username: Optional[str] = None
    pte_vouchername: Optional[str] = None
    pte_password: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_number: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        student_type: Optional[StudentTypeEnum] = Form(None),
        select_student: Optional[int] = Form(None),
        pte_id: Optional[str] = Form(None),
        pte_username: Optional[str] = Form(None),
        pte_vouchername: Optional[str] = Form(None),
        pte_password: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        contact_number: Optional[str] = Form(None),
    ):
        try:
            select_student_int = int(select_student) if select_student not in (None, "", "null") else None
        except ValueError:
            select_student_int = None
        return cls(
            student_type=student_type,
            select_student=select_student_int,
            pte_id=pte_id,
            pte_username=pte_username,
            pte_vouchername=pte_vouchername,
            pte_password=pte_password,
            email=email,
            contact_number=contact_number,
        )


class PTEStudentOut(PTEStudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
