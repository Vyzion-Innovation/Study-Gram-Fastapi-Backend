
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from datetime import date, datetime
from typing import Optional, Literal
from starlette.responses import StreamingResponse
from app.database.session import get_db
from app.auth.dependencies import get_current_user, get_admin_user
from app.models.teacher import Teacher, StatusEnum
from app.models.teacher_attendance import teacher_attendance_association
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut
import csv, io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query



router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.post("/", response_model=TeacherOut)
def create_teacher(data: TeacherCreate = Depends(TeacherCreate.as_form), db: Session = Depends(get_db), user = Depends(get_admin_user)):
    teacher = Teacher(**data.dict())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get("/", response_model=Page[TeacherOut])
def list_teachers(
    name: Optional[str] = Query(None, description="Search by teacher name"),
    start_date: Optional[date] = Query(None, description="Joining start date filter"),
    end_date: Optional[date] = Query(None, description="Joining end date filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    status: Optional[Literal["active", "leave"]] = Query(
        None, description="Filter by teacher status: active or leave"
    ),
    db: Session = Depends(get_db),
    user=Depends(get_admin_user)
):
    query = db.query(Teacher)

    if name:
        query = query.filter(Teacher.name.ilike(f"%{name}%"))

    if start_date and end_date:
        query = query.filter(Teacher.joining_date.between(start_date, end_date))

    if status:
        query = query.filter(Teacher.status == status)

    query = query.order_by(
        asc(Teacher.created_at) if sort_order == "asc" else desc(Teacher.created_at)
    )

    return sqlalchemy_paginate(query)


@router.get("/export")
def export_teachers(
    name: Optional[str] = Query(None, description="Search by teacher name"),
    start_date: Optional[date] = Query(None, description="Joining start date filter"),
    end_date: Optional[date] = Query(None, description="Joining end date filter"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort by created_at"),
    status: Optional[Literal["active", "leave"]] = Query(
        None, description="Filter by teacher status"
    ),
    db: Session = Depends(get_db),
    user=Depends(get_admin_user)
):
    query = db.query(Teacher)

    if name:
        query = query.filter(Teacher.name.ilike(f"%{name}%"))

    if start_date and end_date:
        query = query.filter(Teacher.joining_date.between(start_date, end_date))

    if status:
        query = query.filter(Teacher.status == status)

    query = query.order_by(
        asc(Teacher.created_at) if sort_order == "asc" else desc(Teacher.created_at)
    )

    teachers = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
         "Name", "Email", "DOB", "Marital Status", "Contact Number",
        "WhatsApp Number", "PAN/Adhar", "Joining Date", "Salary", "Department", "Designation",
        "Father/Husband Name", "Father/Husband Contact", "Address",
        "Account Number", "Bank Name", "IFSC Code", "Account Holder Name", "Status", "Created At"
    ])

    for t in teachers:
        writer.writerow([
            t.name,
            t.email,
            t.dob.strftime("%Y-%m-%d") if t.dob else "",
            t.marital_status.value if t.marital_status else "",
            t.contact_number,
            t.whatsapp_number or "",
            t.pan_or_adhar or "",
            t.joining_date.strftime("%Y-%m-%d") if t.joining_date else "",
            t.salary,
            t.department,
            t.designation,
            t.father_or_husband_name or "",
            t.father_or_husband_contact or "",
            t.address or "",
            t.account_number or "",
            t.bank_name or "",
            t.ifsc_code or "",
            t.account_holder_name or "",
            t.status.value if t.status else "",
            t.created_at.strftime("%Y-%m-%d") if t.created_at else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teachers_export.csv"}
    )


@router.get("/{teacher_id}", response_model=TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db), user = Depends(get_admin_user)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/{teacher_id}", response_model=TeacherOut)
def update_teacher(teacher_id: int, data: TeacherUpdate = Depends(TeacherUpdate.as_form), db: Session = Depends(get_db), user = Depends(get_admin_user)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), user = Depends(get_admin_user)):
    # ✅ First: remove entries from association table
    db.execute(
        teacher_attendance_association.delete().where(
            teacher_attendance_association.c.teacher_id == teacher_id
        )
    )

    # ✅ Then: fetch and delete the teacher
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db.delete(teacher)
    db.commit()

    return {"success": True, "message": "Teacher and related attendance data deleted successfully"}

# 🔁 API to change status only
@router.patch("/{teacher_id}/status")
def change_teacher_status(teacher_id: int, new_status: StatusEnum, db: Session = Depends(get_db), user = Depends(get_admin_user)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.status = new_status
    db.commit()
    db.refresh(teacher)
    return {"detail": f"Status changed to {teacher.status}"}

def safe_lower(val):
    return val.lower() if isinstance(val, str) else val

@router.post("/import/")
def import_teachers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    reader = csv.DictReader(io.StringIO(file.file.read().decode()))
    imported = 0

    for row in reader:
        try:
            # Build model with lowercase normalization
            t = Teacher(
                name=safe_lower(row["name"]),
                email=safe_lower(row["email"]),
                dob=datetime.strptime(row["dob"], "%Y-%m-%d").date() if row.get("dob") else None,
                marital_status=row["marital_status"],
                contact_number=row["contact_number"],
                whatsapp_number=row.get("whatsapp_number"),
                pan_or_adhar=safe_lower(row.get("pan_or_adhar")),
                joining_date=datetime.strptime(row["joining_date"], "%Y-%m-%d").date(),
                salary=float(row["salary"]),
                department=safe_lower(row["department"]),
                designation=safe_lower(row["designation"]),
                father_or_husband_name=safe_lower(row.get("father_or_husband_name")),
                father_or_husband_contact=row.get("father_or_husband_contact"),
                address=safe_lower(row.get("address")),
                account_number=row.get("account_number"),
                bank_name=safe_lower(row.get("bank_name")),
                ifsc_code=row.get("ifsc_code"),
                account_holder_name=safe_lower(row.get("account_holder_name")),
                status=row.get("status", "active")
            )
            db.add(t)
            imported += 1

        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Missing column: {e.args[0]}")
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=f"Data format error: {ve}")

    if imported == 0:
        raise HTTPException(status_code=400, detail="No valid rows")

    db.commit()
    return {"message": f"Imported {imported} teachers successfully"}