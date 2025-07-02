from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing_extensions import Literal  # for better compatibility

class ProfileOut(BaseModel):
    name: str
    number: str
    role: str
    address: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...),
        role: str = Form(...)
    ):
        return cls(
            name=name,
            email=email,
            password=password,
            role=role
        )


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    def as_form(
            cls,
            email: EmailStr = Form(...),
            password: str = Form(...),
    ):
        return cls(
            email=email,
            password=password
        )

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    profile: Optional[ProfileOut] = None

    class Config:
        orm_mode = True
