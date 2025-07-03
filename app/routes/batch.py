from fastapi import APIRouter, Depends, HTTPException, Form, Query
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from typing import Literal, Optional
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from app.auth.dependencies import get_admin_user
from app.database.session import get_db
from app.schemas import batch as schemas
from app.models import batch as models, Batch, Course, PaymentDuration
from app.schemas.batch import BatchOut, CourseOut, DurationOut
from app.models.regular_student import RegularStudent

router = APIRouter()


@router.post("/batches/", response_model=schemas.BatchOut)
def create_batch(
    batch: schemas.BatchCreate = Depends(schemas.BatchCreate.as_form),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    new_batch = models.Batch(**batch.dict())
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch


@router.get("/batches/", response_model=Page[BatchOut])
def get_batches(
    sort_order: Literal["asc", "desc"] = Query("desc"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    query = db.query(Batch)

    if search:
        query = query.filter(Batch.name.ilike(f"%{search}%"))

    query = query.order_by(
        asc(Batch.created_at) if sort_order == "asc" else desc(Batch.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/batches/{batch_id}", response_model=BatchOut)
def get_batch_by_id(
    batch_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.get("/batches/{batch_id}/student-count")
def get_student_count_by_batch_id(
    batch_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    # Check if batch exists
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Get count
    count = (
        db.query(func.count(RegularStudent.id))
        .filter(RegularStudent.batch_id == batch_id)
        .scalar()
    )

    return {
        "batch_id": batch.id,
        "batch_name": batch.name,
        "student_count": count
    }


# @router.put("/batches/{batch_id}", response_model=schemas.BatchOut)
# def update_batch(
#     batch_id: int,
#     batch: schemas.BatchUpdate,
#     db: Session = Depends(get_db),
#     _: str = Depends(get_admin_user)
# ):
#     db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
#     if not db_batch:
#         raise HTTPException(status_code=404, detail="Batch not found")
#     for key, value in batch.dict(exclude_unset=True).items():
#         setattr(db_batch, key, value)
#     db.commit()
#     db.refresh(db_batch)
#     return db_batch


@router.post("/courses/", response_model=schemas.CourseOut)
def create_course(
    course: schemas.CourseCreate = Depends(schemas.CourseCreate.as_form),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/courses/", response_model=Page[CourseOut])
def get_courses(
    sort_order: Literal["asc", "desc"] = Query("desc"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    query = db.query(Course)

    if search:
        query = query.filter(Course.course_name.ilike(f"%{search}%"))

    query = query.order_by(
        asc(Course.created_at) if sort_order == "asc" else desc(Course.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/courses/{course_id}", response_model=CourseOut)
def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/durations/", response_model=schemas.DurationOut)
def create_duration(
    duration: schemas.DurationCreate = Depends(schemas.DurationCreate.as_form),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    new_duration = models.PaymentDuration(**duration.dict())
    db.add(new_duration)
    db.commit()
    db.refresh(new_duration)
    return new_duration


@router.get("/durations/", response_model=Page[DurationOut])
def get_durations(
    sort_order: Literal["asc", "desc"] = Query("desc"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    query = db.query(PaymentDuration)

    if search:
        query = query.filter(PaymentDuration.duration_time.ilike(f"%{search}%"))

    query = query.order_by(
        asc(PaymentDuration.created_at) if sort_order == "asc" else desc(PaymentDuration.created_at)
    )

    return sqlalchemy_paginate(query)

@router.get("/durations/{duration_id}", response_model=DurationOut)
def get_duration_by_id(
    duration_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_admin_user)
):
    duration = db.query(PaymentDuration).filter(PaymentDuration.id == duration_id).first()
    if not duration:
        raise HTTPException(status_code=404, detail="Duration not found")
    return duration
