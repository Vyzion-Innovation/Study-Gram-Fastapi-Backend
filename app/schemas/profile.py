from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"

class ProfileBase(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum
    user_id: Optional[int] = None
    business_name: Optional[str] = None
    primary_contact_number: Optional[str] = None
    secondary_contact_number: Optional[str] = None
    secondary_email: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        role: RoleEnum = Form(...),
        user_id: Optional[int] = Form(None),
        business_name: Optional[str] = Form(None),
        primary_contact_number: Optional[str] = Form(None),
        secondary_contact_number: Optional[str] = Form(None),
        secondary_email: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        pincode: Optional[str] = Form(None),
        gst_number: Optional[str] = Form(None),
        address: Optional[str] = Form(None)
    ):
        return cls(
            name=name,
            email=email,
            role=role,
            user_id=user_id,
            business_name=business_name,
            primary_contact_number=primary_contact_number,
            secondary_contact_number=secondary_contact_number,
            secondary_email=secondary_email,
            city=city,
            pincode=pincode,
            gst_number=gst_number,
            address=address
        )


class ProfileCreate(ProfileBase):
    pass


# ✅ Only allow update of editable fields
class ProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    primary_contact_number: Optional[str] = None
    secondary_contact_number: Optional[str] = None
    secondary_email: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        business_name: Optional[str] = Form(None),
        primary_contact_number: Optional[str] = Form(None),
        secondary_contact_number: Optional[str] = Form(None),
        secondary_email: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        pincode: Optional[str] = Form(None),
        gst_number: Optional[str] = Form(None),
        address: Optional[str] = Form(None)
    ):
        return cls(
            business_name=business_name,
            primary_contact_number=primary_contact_number,
            secondary_contact_number=secondary_contact_number,
            secondary_email=secondary_email,
            city=city,
            pincode=pincode,
            gst_number=gst_number,
            address=address
        )


class ProfileOut(ProfileBase):
    id: int

    class Config:
        orm_mode = True
