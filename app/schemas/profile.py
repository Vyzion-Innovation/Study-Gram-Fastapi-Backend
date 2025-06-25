from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional


class ProfileBase(BaseModel):
    name: str
    business_name: str
    primary_contact_number: str
    secondary_contact_number: Optional[str] = None
    primary_email: EmailStr
    secondary_email: Optional[EmailStr] = None
    city: str
    role: str
    pincode: str
    gst_number: Optional[str] = None
    address: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        business_name: str = Form(...),
        primary_contact_number: str = Form(...),
        secondary_contact_number: Optional[str] = Form(None),
        primary_email: EmailStr = Form(...),
        secondary_email: Optional[EmailStr] = Form(None),
        city: str = Form(...),
        role: str = Form(...),
        pincode: str = Form(...),
        gst_number: Optional[str] = Form(None),
        address: str = Form(...)
    ):
        return cls(
            name=name,
            business_name=business_name,
            primary_contact_number=primary_contact_number,
            secondary_contact_number=secondary_contact_number,
            primary_email=primary_email,
            secondary_email=secondary_email,
            city=city,
            role=role,
            pincode=pincode,
            gst_number=gst_number,
            address=address
        )


class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: int

    class Config:
        orm_mode = True
