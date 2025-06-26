from fastapi_pagination import Page
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from app.auth.dependencies import get_admin_user
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.core.security import get_hashed_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.database.session import get_db
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect, func
from sqlalchemy import text
from app.models import (
    User,
    StudentAttendance,
    TeacherAttendance,
    Transaction,
    BasicExpense,
    SalaryExpense,
    RegularStudent,
    PTEStudent,
    Visa,
    DemoStudent,
    Teacher,
    Performance,
    MockTest,
    Batch,
    Course,
    PaymentDuration,
    Profile
)

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



@router.delete("/delete-all-except-admin")
def delete_all_except_admin(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    try:
        # Delete from child to parent (to respect foreign key constraints)
        models_to_delete = [
            StudentAttendance,
            TeacherAttendance,
            Transaction,
            BasicExpense,
            SalaryExpense,
            RegularStudent,
            PTEStudent,
            Visa,
            DemoStudent,
            Performance,
            MockTest,
            Teacher,
            Batch,
            Course,
            PaymentDuration,
            Profile,
        ]

        for model in models_to_delete:
            db.query(model).delete(synchronize_session=False)

        # ✅ Only delete users who are NOT admin
        db.query(User).filter(func.lower(User.role) != 'admin').delete(synchronize_session=False)

        db.commit()
        return {"message": "All non-admin data deleted successfully."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")