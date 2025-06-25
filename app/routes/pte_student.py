
from typing import Optional, Literal
from datetime import date
from sqlalchemy import func, asc, desc

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi.responses import StreamingResponse

from app.models import RegularStudent
from app.schemas.pte_student import  PTEStudentOut, PTEStudentUpdate
from app.auth.dependencies import get_current_user

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
import csv
import io
from sqlalchemy.orm import Session
from app.models.pte_student import PTEStudent
from app.database.session import get_db
from app.schemas.pte_student import PTEStudentCreate

router = APIRouter(prefix="/pte-students", tags=["PTE Students"])


@router.post("/", response_model=PTEStudentOut)
def create_pte_student(data: PTEStudentCreate = Depends(PTEStudentCreate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    new_student = PTEStudent(**data.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/", response_model=Page[PTEStudentOut])
def get_all_pte_students(
    search: Optional[str] = Query(None, description="Search by PTE voucher name"),
    start_date: Optional[date] = Query(None, description="Created at start date filter"),
    end_date: Optional[date] = Query(None, description="Created at end date filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(PTEStudent)

    if search:
        query = query.filter(PTEStudent.pte_vouchername.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(func.date(PTEStudent.created_at).between(start_date, end_date))

    query = query.order_by(
        asc(PTEStudent.created_at) if sort_order == "asc" else desc(PTEStudent.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/export")
def export_pte_students(
    search: Optional[str] = Query(None, description="Search by PTE voucher name"),
    start_date: Optional[date] = Query(None, description="Created at start date filter"),
    end_date: Optional[date] = Query(None, description="Created at end date filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(PTEStudent).outerjoin(PTEStudent.regular_student)

    if search:
        query = query.filter(PTEStudent.pte_vouchername.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(func.date(PTEStudent.created_at).between(start_date, end_date))

    query = query.order_by(
        asc(PTEStudent.created_at) if sort_order == "asc" else desc(PTEStudent.created_at)
    )

    students = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
         "Student Type",
        "Student Name",  # instead of Select Student ID
        "PTE ID",
        "PTE Username",
        "PTE Voucher Name",
        "PTE Password",
        "Email",
        "Contact Number",
        "Created At"
    ])

    for s in students:
        writer.writerow([
            s.student_type,
            s.regular_student.name if s.regular_student else "",  # ✅ FIXED LINE
            s.pte_id,
            s.pte_username,
            s.pte_vouchername,
            s.pte_password,
            s.email,
            s.contact_number,
            s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pte_students_export.csv"}
    )



@router.get("/{pte_student_id}", response_model=PTEStudentOut)
def get_pte_student(pte_student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(PTEStudent).filter(PTEStudent.id == pte_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="PTE Student not found")
    return student


@router.put("/{pte_student_id}", response_model=PTEStudentOut)
def update_pte_student(pte_student_id: int, data: PTEStudentUpdate = Depends(PTEStudentUpdate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(PTEStudent).filter(PTEStudent.id == pte_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="PTE Student not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{pte_student_id}")
def delete_pte_student(pte_student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(PTEStudent).filter(PTEStudent.id == pte_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="PTE Student not found")

    db.delete(student)
    db.commit()
    return {"message": "PTE Student deleted successfully"}


@router.post("/import")
async def import_pte_students_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    students = []

    for row in reader:
        try:
            student_data = {
                "student_type": row["student_type"].lower(),
                "select_student": int(row["select_student"]) if row.get("select_student") else None,
                "pte_id": row["pte_id"],
                "pte_username": row["pte_username"],
                "pte_vouchername": row["pte_vouchername"],
                "pte_password": row["pte_password"],
                "email": row["email"],
                "contact_number": row["contact_number"]
            }

            schema = PTEStudentCreate(**student_data)

            student = PTEStudent(
                student_type=schema.student_type,
                select_student=schema.select_student,
                pte_id=schema.pte_id.lower(),
                pte_username=schema.pte_username.lower(),
                pte_vouchername=schema.pte_vouchername.lower(),
                pte_password=schema.pte_password.lower(),
                email=schema.email.lower(),
                contact_number=schema.contact_number.lower(),
            )
            students.append(student)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in row: {row}. Error: {str(e)}")

    db.add_all(students)
    db.commit()

    return {"message": f"{len(students)} PTE students imported successfully"}