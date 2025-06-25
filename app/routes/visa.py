from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import or_, and_, asc, desc
from datetime import date, datetime
from typing import Optional, Literal

from starlette.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.models import RegularStudent, Course
from app.schemas.visa import VisaCreate, VisaUpdate, VisaOut
import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.visa import Visa
from app.schemas.visa import VisaCreate, VisaTypeEnum, StudentTypeEnum

router = APIRouter(prefix="/visa", tags=["Visa"])


@router.post("/", response_model=VisaOut)
def create_visa(data: VisaCreate = Depends(VisaCreate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    visa = Visa(**data.dict())
    db.add(visa)
    db.commit()
    db.refresh(visa)
    return visa


@router.get("/", response_model=Page[VisaOut])
def list_visas(
    name: Optional[str] = Query(None, description="Search by student name"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Visa)

    # Filter by name
    if name:
        query = query.filter(Visa.name.ilike(f"%{name}%"))

    # Filter by created_at date range using BETWEEN
    if start_date and end_date:
        query = query.filter(Visa.created_at.between(start_date, end_date))
    elif start_date:
        query = query.filter(Visa.created_at >= start_date)
    elif end_date:
        query = query.filter(Visa.created_at <= end_date)

    # Sort by created_at
    query = query.order_by(
        asc(Visa.created_at) if sort_order == "asc" else desc(Visa.created_at)
    )

    return sqlalchemy_paginate(query)



@router.get("/export/csv")
def export_visas_to_csv(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Search by name"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
):
    # Build base query
    query = db.query(Visa)

    # Apply filters
    if name:
        query = query.filter(Visa.name.ilike(f"%{name}%"))

    if start_date:
        query = query.filter(Visa.created_at >= str(start_date))

    if end_date:
        query = query.filter(Visa.created_at <= str(end_date))

    # Sort by created_at
    if sort_order == "asc":
        query = query.order_by(asc(Visa.created_at))
    else:
        query = query.order_by(desc(Visa.created_at))

    visas = query.all()

    # Prepare CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
    "visa_type", "country", "visa_consultant_fee", "visa_process_timing",
        "student_type", "student_id", "name", "marks_10th", "marks_12th",
        "graduation", "other_degree", "course_id", "previous_visa_refusal",
        "refusal_reason", "address", "created_at", "updated_at"
    ])

    # Data rows
    for visa in visas:
        writer.writerow([

            visa.visa_type,
            visa.country,
            visa.visa_consultant_fee,
            visa.visa_process_timing,
            visa.student_type,
            visa.student_id,
            visa.name,
            visa.marks_10th,
            visa.marks_12th,
            visa.graduation,
            visa.other_degree,
            visa.course_id,
            visa.previous_visa_refusal,
            visa.refusal_reason,
            visa.address,
            visa.created_at,
            visa.updated_at
        ])

    output.seek(0)
    filename = f"visa_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

@router.get("/{visa_id}", response_model=VisaOut)
def get_visa(visa_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    visa = db.query(Visa).filter(Visa.id == visa_id).first()
    if not visa:
        raise HTTPException(status_code=404, detail="Visa record not found")
    return visa


@router.put("/{visa_id}", response_model=VisaOut)
def update_visa(visa_id: int, data: VisaUpdate = Depends(VisaUpdate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    visa = db.query(Visa).filter(Visa.id == visa_id).first()
    if not visa:
        raise HTTPException(status_code=404, detail="Visa record not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(visa, key, value)

    db.commit()
    db.refresh(visa)
    return visa


@router.delete("/{visa_id}")
def delete_visa(visa_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    visa = db.query(Visa).filter(Visa.id == visa_id).first()
    if not visa:
        raise HTTPException(status_code=404, detail="Visa record not found")

    db.delete(visa)
    db.commit()
    return {"detail": "Visa record deleted successfully"}


@router.post("/import-visas")
def import_visas(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(content))
    imported = 0
    errors = []

    # Fetch valid IDs for validation
    valid_student_ids = {s.id for s in db.query(RegularStudent.id).all()}
    valid_course_ids = {c.id for c in db.query(Course.id).all()}

    for i, row in enumerate(csv_reader, start=2):  # Header is row 1
        try:
            student_id = int(row["student_id"]) if row["student_id"] else None
            course_id = int(row["course_id"]) if row["course_id"] else None

            # Validate student_id
            if student_id and student_id not in valid_student_ids:
                raise ValueError(f"Invalid student_id on row {i}: {student_id}")

            # Validate course_id
            if course_id and course_id not in valid_course_ids:
                raise ValueError(f"Invalid course_id on row {i}: {course_id}")

            # Construct the VisaCreate object
            visa_data = VisaCreate(
                visa_type=VisaTypeEnum(row["visa_type"].strip().lower()),
                country=row["country"].strip().lower(),
                visa_consultant_fee=int(row["visa_consultant_fee"]),
                visa_process_timing=row["visa_process_timing"].strip().lower(),
                student_type=StudentTypeEnum(row["student_type"].strip().lower()),
                student_id=student_id,
                name=row["name"].strip().lower(),
                marks_10th=int(row["marks_10th"]) if row["marks_10th"] else None,
                marks_12th=int(row["marks_12th"]) if row["marks_12th"] else None,
                graduation=row["graduation"].strip().lower() if row["graduation"] else None,
                other_degree=row["other_degree"].strip().lower() if row["other_degree"] else None,
                course_id=course_id,
                previous_visa_refusal=row["previous_visa_refusal"].strip().lower() == "true",
                refusal_reason=row["refusal_reason"].strip().lower() if row["refusal_reason"] else None,
                address=row["address"].strip().lower(),
            )

            visa = Visa(**visa_data.model_dump())
            db.add(visa)
            imported += 1

        except ValueError as ve:
            errors.append(f"Row {i}: {ve}")
        except Exception as e:
            errors.append(f"Row {i}: Unexpected error: {str(e)}")

    db.commit()

    return {
        "status": "completed",
        "imported": imported,
        "errors": errors
    }
