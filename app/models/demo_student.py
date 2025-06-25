from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

class DemoStudent(Base):
    __tablename__ = "demo_students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    demo_date = Column(Date, nullable=False)
    address = Column(String, nullable=True)

    demo_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    demo_course = relationship("Course")
