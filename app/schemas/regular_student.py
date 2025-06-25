from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from enum import Enum
from fastapi import Form


# ---------- Enums ----------
class StudentStatus(str, Enum):
    active = "active"
    leave = "leave"

class MaritalStatusEnum(str, Enum):
    single = "single"
    married = "married"
    widowed = "widowed"
    divorced = "divorced"


# ---------- Base Validators ----------
class BaseStudentEmailValidator(BaseModel):
    email: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v):
        if v and "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower() if v else v


class LowercaseTextMixin(BaseModel):
    @field_validator("admission_number","name", "email", "father_or_husband_name", "address", "reference", mode="before", check_fields=False)
    @classmethod
    def to_lowercase(cls, v):
        if v and isinstance(v, str):
            return v.lower()
        return v


# ---------- Base Schema ----------
class RegularStudentBase(BaseStudentEmailValidator, LowercaseTextMixin):
    admission_number: str
    admission_date: date
    name: str
    dob: date
    contact_number: str
    father_or_husband_name: str
    father_or_husband_number: str
    address: Optional[str] = None
    marital_status: MaritalStatusEnum
    course_id: int
    batch_id: int
    payment_duration_id: int
    demo_date: Optional[date] = None
    batch_fee_per_month: int
    reference: Optional[str] = None
    previous_visa_refusal: Optional[str] = None
    refusal_reason: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        admission_number: str = Form(...),
        admission_date: date = Form(...),
        name: str = Form(...),
        dob: date = Form(...),
        email: Optional[EmailStr] = Form(None),
        contact_number: str = Form(...),
        father_or_husband_name: str = Form(...),
        father_or_husband_number: str = Form(...),
        address: Optional[str] = Form(None),
        marital_status: MaritalStatusEnum = Form(...),
        course_id: int = Form(...),
        batch_id: int = Form(...),
        payment_duration_id: int = Form(...),
        demo_date: Optional[date] = Form(None),
        batch_fee_per_month: int = Form(...),
        reference: Optional[str] = Form(None),
        previous_visa_refusal: Optional[str] = Form(None),
        refusal_reason: Optional[str] = Form(None),
    ):
        return cls(
            admission_number=admission_number,
            admission_date=admission_date,
            name=name,
            dob=dob,
            email=email,
            contact_number=contact_number,
            father_or_husband_name=father_or_husband_name,
            father_or_husband_number=father_or_husband_number,
            address=address,
            marital_status=marital_status,
            course_id=course_id,
            batch_id=batch_id,
            payment_duration_id=payment_duration_id,
            demo_date=demo_date,
            batch_fee_per_month=batch_fee_per_month,
            reference=reference,
            previous_visa_refusal=previous_visa_refusal,
            refusal_reason=refusal_reason,
        )


# ---------- Create ----------
class RegularStudentCreate(RegularStudentBase):
    pass


# ---------- Update ----------
class RegularStudentUpdate(BaseStudentEmailValidator, LowercaseTextMixin):
    admission_date: Optional[date]
    name: Optional[str]
    dob: Optional[date]
    contact_number: Optional[str]
    father_or_husband_name: Optional[str]
    father_or_husband_number: Optional[str]
    address: Optional[str]
    marital_status: Optional[MaritalStatusEnum] = None
    course_id: Optional[int]
    batch_id: Optional[int]
    payment_duration_id: Optional[int]
    demo_date: Optional[date]
    batch_fee_per_month: Optional[int]
    reference: Optional[str]
    previous_visa_refusal: Optional[str]
    refusal_reason: Optional[str]

    @classmethod
    def as_form(
        cls,
        admission_date: Optional[date] = Form(None),
        name: Optional[str] = Form(None),
        dob: Optional[date] = Form(None),
        email: Optional[EmailStr] = Form(None),
        contact_number: Optional[str] = Form(None),
        father_or_husband_name: Optional[str] = Form(None),
        father_or_husband_number: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        marital_status: Optional[MaritalStatusEnum] = Form(None),
        course_id: Optional[int] = Form(None),
        batch_id: Optional[int] = Form(None),
        payment_duration_id: Optional[int] = Form(None),
        demo_date: Optional[date] = Form(None),
        batch_fee_per_month: Optional[int] = Form(None),
        reference: Optional[str] = Form(None),
        previous_visa_refusal: Optional[str] = Form(None),
        refusal_reason: Optional[str] = Form(None),
    ):
        return cls(
            admission_date=admission_date,
            name=name,
            dob=dob,
            email=email,
            contact_number=contact_number,
            father_or_husband_name=father_or_husband_name,
            father_or_husband_number=father_or_husband_number,
            address=address,
            marital_status=marital_status,
            course_id=course_id,
            batch_id=batch_id,
            payment_duration_id=payment_duration_id,
            demo_date=demo_date,
            batch_fee_per_month=batch_fee_per_month,
            reference=reference,
            previous_visa_refusal=previous_visa_refusal,
            refusal_reason=refusal_reason,
        )


# ---------- Output ----------
class RegularStudentOut(RegularStudentBase):
    id: int
    status: StudentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # <- for Pydantic v2
