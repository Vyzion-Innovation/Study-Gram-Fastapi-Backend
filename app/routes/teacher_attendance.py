from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database.session import get_db
from app.models.teacher import Teacher
from app.models.teacher_attendance import TeacherAttendance
from app.schemas.teacher_attendance import (
    TeacherAttendanceCreate,
    TeacherAttendanceResponse,
    TeacherBase
)

router = APIRouter(prefix="/teacher-attendance", tags=["Teacher Attendance"])

# Get present teachers for a given date (default: today)
@router.get("/", response_model=TeacherAttendanceResponse)
def get_teacher_attendance(
    target_date: date = date.today(),
    db: Session = Depends(get_db)
):
    attendance = db.query(TeacherAttendance).filter(TeacherAttendance.date == target_date).first()
    present_teachers = attendance.present_teachers if attendance else []

    data = [
        TeacherBase(
            id=t.id,
            name=t.name,
            contact_number=t.contact_number
        ) for t in present_teachers
    ]
    return {"data": data}


# Save or update attendance
@router.post("/mark")
def mark_teacher_attendance(
    present_teacher_ids: List[int],
    attendance_date: date = date.today(),
    db: Session = Depends(get_db)
):
    # Get or create attendance record
    attendance = db.query(TeacherAttendance).filter_by(date=attendance_date).first()

    if not attendance:
        attendance = TeacherAttendance(date=attendance_date)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

    # Fetch teacher objects
    teachers = db.query(Teacher).filter(Teacher.id.in_(present_teacher_ids)).all()

    if len(teachers) != len(present_teacher_ids):
        raise HTTPException(status_code=404, detail="One or more teacher IDs not found")

    attendance.present_teachers = teachers  # Overwrite
    db.commit()

    return {
        "message": "Teacher attendance marked successfully",
        "present_teacher_ids": present_teacher_ids
    }