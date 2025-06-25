from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from typing import List, Optional, Literal
from datetime import date, datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from starlette.responses import StreamingResponse
import csv
import io
from sqlalchemy import text
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models import PaymentDuration, Batch, Course
from app.models.regular_student import RegularStudent, StudentStatus, MaritalStatusEnum
from app.schemas.regular_student import RegularStudentCreate, RegularStudentUpdate, RegularStudentOut

router = APIRouter(prefix="/regular-students", tags=["Regular Students"])


@router.post("/", response_model=RegularStudentOut)
def create_regular_student(
    data: RegularStudentCreate = Depends(RegularStudentCreate.as_form),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    student = RegularStudent(**data.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=Page[RegularStudentOut])
def get_students(
    search: Optional[str] = Query(None, description="Search by student name"),
    start_date: Optional[date] = Query(None, description="Admission start date filter"),
    end_date: Optional[date] = Query(None, description="Admission end date filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by admission_date"),
    status: Optional[Literal["active", "leave"]] = Query(None, description="Filter by student status: active or leave"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(RegularStudent)

    if search:
        query = query.filter(RegularStudent.name.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(RegularStudent.admission_date.between(start_date, end_date))

    if status:
        query = query.filter(RegularStudent.status == status)

    query = query.order_by(
        asc(RegularStudent.created_at) if sort_order == "asc" else desc(RegularStudent.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/export")
def export_students(
    search: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    status: Optional[Literal["active", "leave"]] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(RegularStudent).join(RegularStudent.course).join(RegularStudent.batch).join(RegularStudent.payment_duration)

    if search:
        query = query.filter(RegularStudent.name.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(RegularStudent.admission_date.between(start_date, end_date))

    if status:
        query = query.filter(RegularStudent.status == status)

    query = query.order_by(
        asc(RegularStudent.created_at) if sort_order == "asc" else desc(RegularStudent.created_at)
    )

    students = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Admission Number", "Admission Date", "Name", "DOB", "Email", "Contact Number",
        "Father/Husband Name", "Father/Husband Number", "Address", "Marital Status",
        "Course Name", "Batch Name", "Payment Duration", "Demo Date", "Batch Fee/Month",
        "Reference", "Previous Visa Refusal", "Refusal Reason", "Status", "Created At"
    ])

    for s in students:
        writer.writerow([
            s.admission_number,
            s.admission_date.strftime("%Y-%m-%d"),
            s.name,
            s.dob.strftime("%Y-%m-%d"),
            s.email or "",
            s.contact_number,
            s.father_or_husband_name,
            s.father_or_husband_number,
            s.address or "",
            s.marital_status.value,
            s.course.course_name if s.course else "",
            s.batch.name if s.batch else "",
            s.payment_duration.duration_time if s.payment_duration else "",
            s.demo_date.strftime("%Y-%m-%d") if s.demo_date else "",
            s.batch_fee_per_month,
            s.reference or "",
            s.previous_visa_refusal or "",
            s.refusal_reason or "",
            s.status.value,
            s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=regular_students_export.csv"}
    )


@router.get("/{student_id}", response_model=RegularStudentOut)
def get_student_by_id(student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(RegularStudent).filter(RegularStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=RegularStudentOut)
def update_student(student_id: int, data: RegularStudentUpdate = Depends(RegularStudentUpdate.as_form), db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(RegularStudent).filter(RegularStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Step 1: Find student
    student = db.query(RegularStudent).filter(RegularStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Step 2: Remove the student from the attendance association table
    db.execute(
        text("DELETE FROM student_attendance_association WHERE student_id = :student_id"),
        {"student_id": student_id}
    )

    # Step 3: Delete the student
    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


@router.patch("/{student_id}/status")
def change_student_status(student_id: int, new_status: StudentStatus, db: Session = Depends(get_db), user=Depends(get_current_user)):
    student = db.query(RegularStudent).filter(RegularStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    student.status = new_status
    db.commit()
    db.refresh(student)
    return {"detail": f"Status changed to {student.status}"}


def safe_lower(value):
    return value.lower() if isinstance(value, str) else value


@router.post("/import/")
def import_regular_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are allowed.")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    students_to_add = []

    course_ids = {c.id for c in db.query(Course.id).all()}
    batch_ids = {b.id for b in db.query(Batch.id).all()}
    duration_ids = {d.id for d in db.query(PaymentDuration.id).all()}

    for row_num, row in enumerate(reader, start=1):
        try:
            course_id = int(row["course_id"])
            batch_id = int(row["batch_id"])
            payment_duration_id = int(row["payment_duration_id"])

            if course_id not in course_ids:
                raise ValueError(f"Invalid course_id on row {row_num}")
            if batch_id not in batch_ids:
                raise ValueError(f"Invalid batch_id on row {row_num}")
            if payment_duration_id not in duration_ids:
                raise ValueError(f"Invalid payment_duration_id on row {row_num}")

            student = RegularStudent(
                admission_number=safe_lower(row["admission_number"]),
                admission_date=datetime.strptime(row["admission_date"], "%Y-%m-%d").date(),
                name=safe_lower(row["name"]),
                dob=datetime.strptime(row["dob"], "%Y-%m-%d").date(),
                email=safe_lower(row.get("email")) if row.get("email") else None,
                contact_number=row["contact_number"],
                father_or_husband_name=safe_lower(row["father_or_husband_name"]),
                father_or_husband_number=row["father_or_husband_number"],
                address=safe_lower(row.get("address")) if row.get("address") else None,
                marital_status=MaritalStatusEnum(row["marital_status"].lower()),
                course_id=course_id,
                batch_id=batch_id,
                payment_duration_id=payment_duration_id,
                demo_date=datetime.strptime(row["demo_date"], "%Y-%m-%d").date() if row.get("demo_date") else None,
                batch_fee_per_month=int(row["batch_fee_per_month"]),
                reference=safe_lower(row.get("reference")),
                previous_visa_refusal=safe_lower(row.get("previous_visa_refusal")),
                refusal_reason=safe_lower(row.get("refusal_reason")),
                status=StudentStatus.active
            )

            students_to_add.append(student)

        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing column: {e.args[0]} on row {row_num}")
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=f"Data format issue on row {row_num}: {ve}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error on row {row_num}: {str(e)}")

    if not students_to_add:
        raise HTTPException(status_code=400, detail="No valid data found in the CSV.")

    db.bulk_save_objects(students_to_add)
    db.commit()

    return {"message": f"Imported {len(students_to_add)} regular students successfully."}
