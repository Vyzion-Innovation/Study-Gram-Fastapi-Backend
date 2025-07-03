from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import desc, asc, func
from starlette.responses import StreamingResponse
from typing import Literal
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models import Course
from app.models.demo_student import DemoStudent
from app.schemas.demo_student import DemoStudentCreate, DemoStudentUpdate, DemoStudentOut
from fastapi import File, UploadFile
import csv
import io

router = APIRouter(prefix="/demo-students", tags=["Demo Students"])


@router.post("/", response_model=DemoStudentOut)
def create_demo_student(data: DemoStudentCreate = Depends(DemoStudentCreate.as_form), db: Session = Depends(get_db),
                        user=Depends(get_current_user)):
    student = DemoStudent(**data.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/export")
def export_demo_students(
        search: Optional[str] = Query(None, description="Search by name"),
        start_date: Optional[date] = Query(None, description="Demo date start filter"),
        end_date: Optional[date] = Query(None, description="Demo date end filter"),
        sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order for demo_date"),
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    query = db.query(DemoStudent).join(DemoStudent.demo_course)

    if search:
        query = query.filter(DemoStudent.name.ilike(f"%{search}%"))

    if start_date and end_date:
        query = query.filter(DemoStudent.demo_date.between(start_date, end_date))

    query = query.order_by(
        asc(DemoStudent.created_at) if sort_order == "asc" else desc(DemoStudent.created_at)
    )

    students = query.all()

    # CSV Export
    output = io.StringIO()
    writer = csv.writer(output)

    # Header without 'ID', with 'Course Name'
    writer.writerow(["Name", "Email", "Contact Number", "Demo Date", "Address", "Course Name", "Created At"])

    # Rows
    for s in students:
        writer.writerow([
            s.name,
            s.email or "",
            s.contact_number or "",
            s.demo_date.strftime("%Y-%m-%d"),
            s.address or "",
            s.demo_course.course_name if s.demo_course else "",
            s.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=demo_students_export.csv"}
    )

#
# @router.get("/{student_id}", response_model=DemoStudentOut)
# def get_demo_student_by_id(student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     student = db.query(DemoStudent).filter(DemoStudent.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Demo student not found")
#     return student
#
#
# from typing import Literal
#
#
# @router.get("/", response_model=Page[DemoStudentOut])
# def get_demo_students(
#         search: Optional[str] = Query(None, description="Search by name"),
#         start_date: Optional[date] = Query(None, description="Demo date start filter"),
#         end_date: Optional[date] = Query(None, description="Demo date end filter"),
#         sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order for demo_date"),
#         db: Session = Depends(get_db),
#         user=Depends(get_current_user)
# ):
#     query = db.query(DemoStudent)
#
#     if search:
#         query = query.filter(DemoStudent.name.ilike(f"%{search}%"))
#
#     if start_date and end_date:
#         query = query.filter(DemoStudent.demo_date.between(start_date, end_date))
#
#     query = query.order_by(
#         asc(DemoStudent.created_at) if sort_order == "asc" else desc(DemoStudent.created_at)
#     )
#
#     return sqlalchemy_paginate(query)
#
#
# @router.put("/{student_id}", response_model=DemoStudentOut)
# def update_demo_student(
#         student_id: int,
#         data: DemoStudentUpdate = Depends(DemoStudentUpdate.as_form),  # <-- key change here
#         db: Session = Depends(get_db),
#         user=Depends(get_current_user)
# ):
#     student = db.query(DemoStudent).filter(DemoStudent.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Demo student not found")
#
#     for key, value in data.dict(exclude_unset=True).items():
#         setattr(student, key, value)
#
#     db.commit()
#     db.refresh(student)
#     return student
#
#
# @router.delete("/{student_id}")
# def delete_demo_student(student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     student = db.query(DemoStudent).filter(DemoStudent.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Demo student not found")
#
#     db.delete(student)
#     db.commit()
#     return {"message": "Demo student deleted successfully"}
#
#
# @router.post("/import/")
# def import_demo_students(
#         file: UploadFile = File(...),
#         db: Session = Depends(get_db),
#         user=Depends(get_current_user)
# ):
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are allowed.")
#
#     content = file.file.read().decode("utf-8")
#     reader = csv.DictReader(io.StringIO(content))
#
#     imported_count = 0
#
#     def safe_lower(value):
#         return value.lower() if isinstance(value, str) else value
#
#     for row in reader:
#         try:
#             # Check if demo_course_id exists
#             demo_course_id = int(row["demo_course_id"])
#             course = db.query(Course).filter(Course.id == demo_course_id).first()
#             if not course:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Invalid demo_course_id: {demo_course_id}. No such course found."
#                 )
#
#             student = DemoStudent(
#                 name=safe_lower(row["name"]),
#                 email=safe_lower(row.get("email")),
#                 contact_number=row.get("contact_number"),
#                 demo_date=datetime.strptime(row["demo_date"], "%Y-%m-%d").date(),
#                 address=safe_lower(row.get("address")),
#                 demo_course_id=demo_course_id
#             )
#             db.add(student)
#             imported_count += 1
#
#         except KeyError as e:
#             raise HTTPException(status_code=400, detail=f"Missing column: {e}")
#         except ValueError as ve:
#             raise HTTPException(status_code=400, detail=f"Data format issue: {ve}")
#
#     if imported_count == 0:
#         raise HTTPException(status_code=400, detail="No valid data found in the CSV.")
#
#     db.commit()
#
#     return {"message": f"Imported {imported_count} demo students successfully."}
