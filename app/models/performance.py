

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    student_type = Column(String, nullable=False)
    select_student = Column(Integer, ForeignKey("regular_students.id"), nullable=True)
    name = Column(String, nullable=False,)
    admission_number = Column(String, nullable=False, unique=True)
    test_date = Column(Date, nullable=False)
    speaking = Column(String, nullable=True)
    writing = Column(String, nullable=True)
    listening = Column(String, nullable=True)
    reading = Column(String, nullable=True)
    overall = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    regular_student = relationship("RegularStudent", backref="performance")
