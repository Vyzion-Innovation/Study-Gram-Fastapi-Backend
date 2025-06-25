

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

class MockTest(Base):
    __tablename__ = "mocktest"

    id = Column(Integer, primary_key=True, index=True)
    student_type = Column(String, nullable=False)
    select_student = Column(Integer, ForeignKey("regular_students.id"), nullable=True)
    name = Column(String, nullable=False,)
    admission_number = Column(String, nullable=False, unique=True)
    test_date = Column(Date, nullable=False)
    speaking = Column(String, nullable=False)
    writing = Column(String, nullable=False)
    listening = Column(String, nullable=False)
    reading = Column(String, nullable=False)
    overall = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    regular_student = relationship("RegularStudent", backref="mocktest")
