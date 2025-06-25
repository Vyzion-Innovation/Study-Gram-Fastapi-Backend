from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum
from fastapi import Form

# -------------------- Enums --------------------
class MaritalStatusEnum(str, Enum):
    single = "single"
    married = "married"
    widowed = "widowed"
    divorced = "divorced"

class StatusEnum(str, Enum):
    active = "active"
    leave = "leave"

# -------------------- Lowercase Mixin --------------------
class LowercaseTextMixin(BaseModel):
    @field_validator(
        "name", "email", "pan_or_adhar",
        "department", "designation", "father_or_husband_name",
        "address", "bank_name", "account_holder_name",
        mode="before", check_fields=False
    )
    @classmethod
    def lowercase_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

# -------------------- Base Schema --------------------
class TeacherBase(LowercaseTextMixin):
    name: str
    email: EmailStr
    dob: Optional[date] = None
    marital_status: MaritalStatusEnum
    contact_number: str
    whatsapp_number: Optional[str] = None
    pan_or_adhar: Optional[str] = None
    joining_date: date
    salary: float
    department: str
    designation: str
    father_or_husband_name: Optional[str] = None
    father_or_husband_contact: Optional[str] = None
    address: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        dob: Optional[date] = Form(None),
        marital_status: MaritalStatusEnum = Form(...),
        contact_number: str = Form(...),
        whatsapp_number: Optional[str] = Form(None),
        pan_or_adhar: Optional[str] = Form(None),
        joining_date: date = Form(...),
        salary: float = Form(...),
        department: str = Form(...),
        designation: str = Form(...),
        father_or_husband_name: Optional[str] = Form(None),
        father_or_husband_contact: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        account_number: Optional[str] = Form(None),
        bank_name: Optional[str] = Form(None),
        ifsc_code: Optional[str] = Form(None),
        account_holder_name: Optional[str] = Form(None),
    ) -> "TeacherBase":
        return cls(
            name=name, email=email, dob=dob, marital_status=marital_status,
            contact_number=contact_number, whatsapp_number=whatsapp_number,
            pan_or_adhar=pan_or_adhar, joining_date=joining_date,
            salary=salary, department=department, designation=designation,
            father_or_husband_name=father_or_husband_name,
            father_or_husband_contact=father_or_husband_contact,
            address=address, account_number=account_number,
            bank_name=bank_name, ifsc_code=ifsc_code,
            account_holder_name=account_holder_name
        )

# -------------------- Create Schema --------------------
class TeacherCreate(TeacherBase):
    pass

# -------------------- Update Schema --------------------
class TeacherUpdate(LowercaseTextMixin):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    dob: Optional[date] = None
    marital_status: Optional[MaritalStatusEnum] = None
    contact_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    pan_or_adhar: Optional[str] = None
    joining_date: Optional[date] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    father_or_husband_name: Optional[str] = None
    father_or_husband_contact: Optional[str] = None
    address: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        dob: Optional[date] = Form(None),
        marital_status: Optional[MaritalStatusEnum] = Form(None),
        contact_number: Optional[str] = Form(None),
        whatsapp_number: Optional[str] = Form(None),
        pan_or_adhar: Optional[str] = Form(None),
        joining_date: Optional[date] = Form(None),
        salary: Optional[float] = Form(None),
        department: Optional[str] = Form(None),
        designation: Optional[str] = Form(None),
        father_or_husband_name: Optional[str] = Form(None),
        father_or_husband_contact: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        account_number: Optional[str] = Form(None),
        bank_name: Optional[str] = Form(None),
        ifsc_code: Optional[str] = Form(None),
        account_holder_name: Optional[str] = Form(None),
    ) -> "TeacherUpdate":
        return cls(**{k: v for k, v in locals().items() if k != "cls"})

# -------------------- Output Schema --------------------
class TeacherOut(TeacherBase):
    id: int
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # for ORM support in Pydantic v2
