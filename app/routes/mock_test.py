from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from typing import Optional, Literal
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from datetime import date
import csv
import io
from fastapi import Response
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.mock_test import MockTest
from app.schemas.mock_test import MockTestCreate, MockTestUpdate, MockTestOut

router = APIRouter(prefix="/mocktest", tags=["Mock Test"])


@router.post("/", response_model=MockTestOut)
def create_mocktest(
    data: MockTestCreate = Depends(MockTestCreate.as_form),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    mocktest = MockTest(**data.dict())
    db.add(mocktest)
    db.commit()
    db.refresh(mocktest)
    return mocktest


@router.get("/", response_model=Page[MockTestOut])
def list_mocktests(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    name: Optional[str] = Query(None),
    test_date: Optional[date] = Query(None),
    student_type: Optional[str] = Query(None),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at")
):
    query = db.query(MockTest)

    if student_type:
        query = query.filter(MockTest.student_type == student_type)
    if name:
        query = query.filter(MockTest.name.ilike(f"%{name}%"))
    if test_date:
        query = query.filter(MockTest.test_date == test_date)

    query = query.order_by(
        asc(MockTest.created_at) if sort_order == "asc" else desc(MockTest.created_at)
    )

    return sqlalchemy_paginate(query)

@router.get("/export/csv")
def export_mocktests_csv(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),

    name: Optional[str] = Query(None),
    test_date: Optional[date] = Query(None),
):
    query = db.query(MockTest).outerjoin(MockTest.regular_student)


    if name:
        query = query.filter(MockTest.name.ilike(f"%{name}%"))
    if test_date:
        query = query.filter(MockTest.test_date == test_date)

    results = query.order_by(desc(MockTest.created_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
         "Student Type", "Student Name", "Name",
        "Admission Number", "Test Date", "Speaking",
        "Writing", "Listening", "Reading", "Overall", "Created At"
    ])

    for m in results:
        writer.writerow([
            m.student_type,
            m.regular_student.name if m.regular_student else "",
            m.name,
            m.admission_number,
            m.test_date.strftime("%Y-%m-%d") if m.test_date else "",
            m.speaking,
            m.writing,
            m.listening,
            m.reading,
            m.overall,
            m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else ""
        ])

    output.seek(0)
    headers = {
        "Content-Disposition": "attachment; filename=mocktests_export.csv"
    }
    return Response(content=output.getvalue(), media_type="text/csv", headers=headers)


@router.get("/{mocktest_id}", response_model=MockTestOut)
def get_mocktest(mocktest_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    mocktest = db.query(MockTest).filter(MockTest.id == mocktest_id).first()
    if not mocktest:
        raise HTTPException(status_code=404, detail="MockTest not found")
    return mocktest


@router.put("/{mocktest_id}", response_model=MockTestOut)
def update_mocktest(
    mocktest_id: int,
    data: MockTestUpdate = Depends(MockTestUpdate.as_form),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    mocktest = db.query(MockTest).filter(MockTest.id == mocktest_id).first()
    if not mocktest:
        raise HTTPException(status_code=404, detail="MockTest not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(mocktest, key, value)

    db.commit()
    db.refresh(mocktest)
    return mocktest


@router.delete("/{mocktest_id}")
def delete_mocktest(mocktest_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    mocktest = db.query(MockTest).filter(MockTest.id == mocktest_id).first()
    if not mocktest:
        raise HTTPException(status_code=404, detail="MockTest not found")
    db.delete(mocktest)
    db.commit()
    return {"message": "MockTest deleted successfully"}


