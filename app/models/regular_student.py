# app/database/models/regular_student.py
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.database.config import Base
import enum
from datetime import datetime

class StudentStatus(str, enum.Enum):
    active = "active"
    leave = "leave"

class MaritalStatusEnum(str, enum.Enum):
    single = "single"
    married = "married"
    widowed = "widowed"
    divorced = "divorced"

class RegularStudent(Base):
    __tablename__ = "regular_students"

    id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String, nullable=False, unique=True)
    admission_date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    email = Column(String, nullable=True)
    contact_number = Column(String, nullable=False)
    father_or_husband_name = Column(String, nullable=False)
    father_or_husband_number = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    payment_duration_id = Column(Integer, ForeignKey("payment_durations.id"), nullable=False)

    demo_date = Column(Date, nullable=True)
    batch_fee_per_month = Column(Integer, nullable=False)
    reference = Column(String, nullable=True)

    previous_visa_refusal = Column(String, nullable=True)  # 'yes' or 'no'
    refusal_reason = Column(Text, nullable=True)
    status = Column(Enum(StudentStatus), default=StudentStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course")
    batch = relationship("Batch", back_populates="students")

    payment_duration = relationship("PaymentDuration")
    # in RegularStudent model
    transactions = relationship("Transaction", back_populates="student", cascade="all, delete-orphan")
