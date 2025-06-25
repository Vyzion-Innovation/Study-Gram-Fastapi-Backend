from pydantic import BaseModel, Field, model_validator
from fastapi import Form
from typing import Optional
from datetime import datetime
from enum import Enum


class VisaTypeEnum(str, Enum):
    student = "student"
    work = "work"
    visitor = "visitor"


class StudentTypeEnum(str, Enum):
    new_student = "new_student"
    existing_student = "existing_student"


class VisaBase(BaseModel):
    visa_type: VisaTypeEnum
    country: str
    visa_consultant_fee: int
    visa_process_timing: str
    student_type: StudentTypeEnum
    student_id: Optional[int] = None
    name: str
    marks_10th: Optional[int] = None
    marks_12th: Optional[int] = None
    graduation: Optional[str] = None
    other_degree: Optional[str] = None
    course_id: Optional[int] = None
    previous_visa_refusal: bool = False
    refusal_reason: Optional[str] = None
    address: str

    @model_validator(mode="after")
    def validate_fields(cls, values):
        if values.student_type == StudentTypeEnum.existing_student and values.student_id is None:
            raise ValueError("student_id is required for existing students")
        if values.student_type == StudentTypeEnum.new_student and values.student_id is not None:
            raise ValueError("student_id must be null for new students")
        return values

    @model_validator(mode="after")
    def convert_strings_to_lowercase(cls, values):
        lowercase_fields = [
            "country",
            "visa_process_timing",
            "name",
            "graduation",
            "other_degree",
            "refusal_reason",
            "address",
        ]
        for field in lowercase_fields:
            val = getattr(values, field, None)
            if isinstance(val, str):
                setattr(values, field, val.lower())
        return values

    @classmethod
    def as_form(
        cls,
        visa_type: VisaTypeEnum = Form(...),
        country: str = Form(...),
        visa_consultant_fee: int = Form(...),
        visa_process_timing: str = Form(...),
        student_type: StudentTypeEnum = Form(...),
        student_id: Optional[int] = Form(None),
        name: str = Form(...),
        marks_10th: Optional[int] = Form(None),
        marks_12th: Optional[int] = Form(None),
        graduation: Optional[str] = Form(None),
        other_degree: Optional[str] = Form(None),
        course_id: Optional[int] = Form(None),
        previous_visa_refusal: bool = Form(False),
        refusal_reason: Optional[str] = Form(None),
        address: str = Form(...)
    ):
        try:
            select_student_int = int(student_id) if student_id not in (None, "", "null") else None
        except ValueError:
            select_student_int = None
        return cls(
            visa_type=visa_type,
            country=country,
            visa_consultant_fee=visa_consultant_fee,
            visa_process_timing=visa_process_timing,
            student_type=student_type,
            student_id=select_student_int,
            name=name,
            marks_10th=marks_10th,
            marks_12th=marks_12th,
            graduation=graduation,
            other_degree=other_degree,
            course_id=course_id,
            previous_visa_refusal=previous_visa_refusal,
            refusal_reason=refusal_reason,
            address=address
        )


class VisaCreate(VisaBase):
    pass


class VisaUpdate(VisaBase):  # ✅ Add this class
    pass


class VisaOut(VisaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
