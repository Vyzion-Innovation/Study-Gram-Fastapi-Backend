from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.config import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    business_name = Column(String, nullable=False)
    primary_contact_number = Column(String, nullable=False)
    secondary_contact_number = Column(String, nullable=True)
    primary_email = Column(String, nullable=False)
    secondary_email = Column(String, nullable=True)
    city = Column(String, nullable=False)
    role = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    gst_number = Column(String, nullable=True)
    address = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="profile")
