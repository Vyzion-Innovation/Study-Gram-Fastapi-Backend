from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.config import Base

class BasicExpense(Base):
    __tablename__ = "basic_expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SalaryExpense(Base):
    __tablename__ = "salary_expenses"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    working_days = Column(Integer, nullable=False)
    salary_amount = Column(Float, nullable=False)
    salary_month = Column(Date, nullable=False)  # Changed to Date
    salary_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    teacher = relationship("Teacher", back_populates="salary_expenses")
