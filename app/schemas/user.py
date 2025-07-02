from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

# ✅ Enum for limited roles
class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"

# ✅ Used in ProfileOut for nested response
class ProfileOut(BaseModel):
    name: str
    role: str
    address: str
    class Config:
        orm_mode = True

# ✅ For creating new users via form
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum  # Only admin or manager allowed

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        role: RoleEnum = Form(...)  # Enforced via Enum
    ):
        return cls(name=name, email=email, password=password, role=role)

# ✅ For login form
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(...)
    ):
        return cls(email=email, password=password)

# ✅ For returning user info
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    profile: Optional[ProfileOut] = None

    class Config:
        orm_mode = True
