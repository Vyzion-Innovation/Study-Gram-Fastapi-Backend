from sqlalchemy import Column, Integer, String, Date, Enum, Float
from app.database.config import Base
from datetime import datetime
import enum
from sqlalchemy.orm import relationship

from app.models.teacher_attendance import teacher_attendance_association


class MaritalStatusEnum(str, enum.Enum):
    single = "single"
    married = "married"
    widowed = "widowed"
    divorced = "divorced"

class StatusEnum(str, enum.Enum):
    active = "active"
    leave = "leave"

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    dob = Column(Date, nullable=True)
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False)
    contact_number = Column(String, nullable=False)
    whatsapp_number = Column(String, nullable=True)
    pan_or_adhar = Column(String, nullable=True)
    joining_date = Column(Date, nullable=False)
    salary = Column(Float, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    father_or_husband_name = Column(String, nullable=True)
    father_or_husband_contact = Column(String, nullable=True)
    address = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.active)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    salary_expenses = relationship(
        "SalaryExpense",
        back_populates="teacher",
        cascade="all, delete"
    )
    attendances = relationship(
        "TeacherAttendance",
        secondary=teacher_attendance_association,
        passive_deletes=True
    )
