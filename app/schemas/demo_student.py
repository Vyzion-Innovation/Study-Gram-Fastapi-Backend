from pydantic import BaseModel, EmailStr, validator, field_validator
from typing import Optional
from datetime import date, datetime
from fastapi import Form

# -------------------- Lowercase Mixin --------------------
class LowercaseTextMixin(BaseModel):
    @field_validator("name", "email", "address", mode="before", check_fields=False)
    @classmethod
    def lowercase_fields(cls, v):
        if v and isinstance(v, str):
            return v.lower()
        return v

# -------------------- Base --------------------
class DemoStudentBase(LowercaseTextMixin):
    name: str
    email: Optional[str] = None
    contact_number: Optional[str] = None
    demo_date: date
    address: Optional[str] = None
    demo_course_id: int

    @validator("email")
    def validate_email(cls, v):
        if v is not None and v != "":
            if "@" not in v:
                raise ValueError("Invalid email address")
        return v

    @staticmethod
    def as_form(
        name: str = Form(...),
        email: Optional[EmailStr] = Form(None),
        contact_number: Optional[str] = Form(None),
        demo_date: date = Form(...),
        address: Optional[str] = Form(None),
        demo_course_id: int = Form(...)
    ) -> "DemoStudentBase":
        return DemoStudentBase(
            name=name,
            email=email,
            contact_number=contact_number,
            demo_date=demo_date,
            address=address,
            demo_course_id=demo_course_id
        )

# -------------------- Create --------------------
class DemoStudentCreate(DemoStudentBase):
    @staticmethod
    def as_form(
        name: str = Form(...),
        email: Optional[EmailStr] = Form(None),
        contact_number: Optional[str] = Form(None),
        demo_date: date = Form(...),
        address: Optional[str] = Form(None),
        demo_course_id: int = Form(...)
    ) -> "DemoStudentCreate":
        return DemoStudentCreate(
            name=name,
            email=email,
            contact_number=contact_number,
            demo_date=demo_date,
            address=address,
            demo_course_id=demo_course_id
        )

# -------------------- Update --------------------
class DemoStudentUpdate(LowercaseTextMixin):
    name: Optional[str]
    email: Optional[EmailStr]
    contact_number: Optional[str]
    demo_date: Optional[date]
    address: Optional[str]
    demo_course_id: Optional[int]

    @staticmethod
    def as_form(
        name: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        contact_number: Optional[str] = Form(None),
        demo_date: Optional[date] = Form(None),
        address: Optional[str] = Form(None),
        demo_course_id: Optional[int] = Form(None)
    ) -> "DemoStudentUpdate":
        return DemoStudentUpdate(
            name=name,
            email=email,
            contact_number=contact_number,
            demo_date=demo_date,
            address=address,
            demo_course_id=demo_course_id
        )

# -------------------- Output --------------------
class DemoStudentOut(DemoStudentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
