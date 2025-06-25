from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAEnum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base
import enum

class VisaTypeEnum(str, enum.Enum):
    student = "student"
    work = "work"
    visitor = "visitor"

class StudentTypeEnum(str, enum.Enum):
    new_student = "new_student"
    existing_student = "existing_student"

class Visa(Base):
    __tablename__ = "visas"

    id = Column(Integer, primary_key=True, index=True)
    visa_type = Column(SQLAEnum(VisaTypeEnum), nullable=False)
    country = Column(String, nullable=False)
    visa_consultant_fee = Column(Integer, nullable=False)
    visa_process_timing = Column(String, nullable=False)
    student_type = Column(SQLAEnum(StudentTypeEnum), nullable=False)
    student_id = Column(Integer, ForeignKey("regular_students.id"), nullable=True)  # 👈 Conditional
    name = Column(String, nullable=False)
    marks_10th = Column(Integer)
    marks_12th = Column(Integer)
    graduation = Column(String)
    other_degree = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    previous_visa_refusal = Column(Boolean, default=False)
    refusal_reason = Column(Text, nullable=True)
    address = Column(String, nullable=False)

    created_at = Column(String, default=datetime.utcnow)
    updated_at = Column(String, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", backref="visas")
    student = relationship("RegularStudent", backref="visas")
