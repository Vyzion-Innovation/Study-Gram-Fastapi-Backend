from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_admin_user
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.core.security import get_hashed_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.session import get_db
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

router = APIRouter()


@router.post("/users/create", response_model=UserOut, dependencies=[Depends(get_admin_user)])
def create_user(user: UserCreate = Depends(UserCreate.as_form), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_hashed_password(user.password)
    new_user = User(
        name=user.name,  # ✅ Include name
        email=user.email,
        password=hashed_password,
        role=user.role.lower()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/managers", response_model=Page[UserOut], dependencies=[Depends(get_admin_user)])
def get_managers(db: Session = Depends(get_db)):
    query = db.query(User).filter(User.role == "manager")
    return sqlalchemy_paginate(query)


@router.delete("/users/{user_id}")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin_user=Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
