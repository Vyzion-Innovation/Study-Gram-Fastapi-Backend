import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import desc, asc
from starlette.responses import StreamingResponse

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.performance import Performance
from app.schemas.performance import PerformanceCreate, PerformanceUpdate, PerformanceOut
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.post("/", response_model=PerformanceOut)
def create_performance(data: PerformanceCreate = Depends(PerformanceCreate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    performance = Performance(**data.dict())
    db.add(performance)
    db.commit()
    db.refresh(performance)
    return performance

from typing import Optional, Literal
from fastapi import Query

@router.get("/", response_model=Page[PerformanceOut])
def get_performances(
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Performance)

    if search:
        query = query.filter(Performance.name.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(Performance.test_date.between(start_date, end_date))

    query = query.order_by(
        asc(Performance.created_at) if sort_order == "asc" else desc(Performance.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/export")
def export_performances(
    search: Optional[str] = Query(None, description="Search by student name"),
    start_date: Optional[date] = Query(None, description="Test date start filter"),
    end_date: Optional[date] = Query(None, description="Test date end filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order for created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Performance).outerjoin(Performance.regular_student)

    if search:
        query = query.filter(Performance.name.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(Performance.test_date.between(start_date, end_date))

    query = query.order_by(
        asc(Performance.created_at) if sort_order == "asc" else desc(Performance.created_at)
    )

    performances = query.all()

    # CSV generation
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student Name", "Admission Number", "Test Date",
        "Speaking", "Writing", "Listening", "Reading", "Overall",
        "Created At"
    ])

    for p in performances:
        writer.writerow([
            p.regular_student.name if p.regular_student else p.name,
            p.admission_number,
            p.test_date.strftime("%Y-%m-%d") if p.test_date else "",
            p.speaking or "",
            p.writing or "",
            p.listening or "",
            p.reading or "",
            p.overall or "",
            p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=performances_export.csv"}
    )

@router.get("/{performance_id}", response_model=PerformanceOut)
def get_performance(performance_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    return performance

@router.put("/{performance_id}", response_model=PerformanceOut)
def update_performance(performance_id: int, data: PerformanceUpdate = Depends(PerformanceUpdate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(performance, key, value)

    db.commit()
    db.refresh(performance)
    return performance

@router.delete("/{performance_id}")
def delete_performance(performance_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")

    db.delete(performance)
    db.commit()
    return {"message": "Performance deleted successfully"}
