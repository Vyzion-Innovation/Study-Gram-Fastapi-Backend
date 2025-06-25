from sqlalchemy import Column, Integer, Float, ForeignKey, Date, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("regular_students.id", ondelete="CASCADE"))
    amount_paid = Column(Float, nullable=False)
    pending_amount = Column(Float, nullable=True)  # <-- allow nulls since it's calculated
    payment_method = Column(String, nullable=False)  # <-- this should always be passed manually
    payment_month_start = Column(Date, nullable=False)
    payment_month_end = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("RegularStudent", back_populates="transactions")
