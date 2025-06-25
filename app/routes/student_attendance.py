from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database.session import get_db
from app.models.student_attendance import StudentAttendance, student_attendance_association
from app.models.regular_student import RegularStudent
from app.models.batch import Batch

router = APIRouter(prefix="/attendance", tags=["Student Attendance"])

@router.get("/students-by-batch")
def get_students_by_batch(
    batch_id: int,
    db: Session = Depends(get_db)
):
    students = db.query(RegularStudent).filter(RegularStudent.batch_id == batch_id).all()

    data = [
        {
            "id": student.id,
            "name": student.name,
            "admission_number": student.admission_number
        } for student in students
    ]

    return JSONResponse(content={"data": data})

# Save or update attendance
@router.post("/mark")
def mark_attendance(
    batch_id: int,
    present_student_ids: List[int],
    attendance_date: date = date.today(),
    db: Session = Depends(get_db)
):
    # 1. Check batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    # 2. Fetch students and validate
    students = db.query(RegularStudent).filter(
        RegularStudent.id.in_(present_student_ids),
        RegularStudent.batch_id == batch_id
    ).all()

    if len(students) != len(present_student_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more student IDs are invalid or don't belong to the batch"
        )

    # 3. Get or create attendance record
    attendance = db.query(StudentAttendance).filter_by(batch_id=batch_id, date=attendance_date).first()
    if not attendance:
        attendance = StudentAttendance(batch_id=batch_id, date=attendance_date)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

    # 4. Update attendance record
    attendance.present_students = students
    db.commit()

    return {"message": "Attendance marked successfully", "present_ids": present_student_ids}


@router.get("/present-students", response_model=List[int])
def get_present_students(
    batch_id: int = Query(...),
    date_value: date = Query(default=date.today()),
    db: Session = Depends(get_db)
):
    attendance = db.query(StudentAttendance).filter_by(batch_id=batch_id, date=date_value).first()
    if not attendance:
        return []

    return JSONResponse(content={"data": [student.id for student in attendance.present_students]})

# Get all students of a specific batch
from fastapi.responses import JSONResponse