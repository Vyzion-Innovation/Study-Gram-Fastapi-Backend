from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

class PTEStudent(Base):
    __tablename__ = "pte_students"

    id = Column(Integer, primary_key=True, index=True)
    student_type = Column(String, nullable=False)
    select_student = Column(Integer, ForeignKey("regular_students.id"), nullable=True)

    pte_id = Column(String, nullable=False, unique=True)
    pte_username = Column(String, nullable=False)
    pte_vouchername = Column(String, nullable=False)
    pte_password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    regular_student = relationship("RegularStudent", backref="pte_students")
