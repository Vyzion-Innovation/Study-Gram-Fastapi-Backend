from sqlalchemy import Column, Integer, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.config import Base

# Association table for teacher attendance
teacher_attendance_association = Table(
    "teacher_attendance_association",
    Base.metadata,
    Column("attendance_id", Integer, ForeignKey("teacher_attendances.id", ondelete="CASCADE")),
    Column("teacher_id", Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
)


class TeacherAttendance(Base):
    __tablename__ = "teacher_attendances"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)


    present_teachers = relationship(
        "Teacher",
        secondary=teacher_attendance_association,
        passive_deletes=True
    )