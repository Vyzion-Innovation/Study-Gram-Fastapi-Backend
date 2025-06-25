from sqlalchemy import Column, Integer, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.config import Base

# Corrected Association Table (use regular_students)
student_attendance_association = Table(
    "student_attendance_association",
    Base.metadata,
    Column("attendance_id", Integer, ForeignKey("student_attendances.id")),
    Column("student_id", Integer, ForeignKey("regular_students.id"))  # Updated here
)

class StudentAttendance(Base):
    __tablename__ = "student_attendances"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    date = Column(Date, nullable=False)

    # Use RegularStudent for relationship
    present_students = relationship(
        "RegularStudent",  # Updated here
        secondary=student_attendance_association
    )
