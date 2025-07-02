from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.config import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    business_name = Column(String, nullable=True, default="")
    primary_contact_number = Column(String, nullable=True, default="")
    secondary_contact_number = Column(String, nullable=True, default="")
    email = Column(String, nullable=False)
    secondary_email = Column(String, nullable=True, default="")
    city = Column(String, nullable=True, default="")
    role = Column(String, nullable=False)
    pincode = Column(String, nullable=True, default="")
    gst_number = Column(String, nullable=True, default="")
    address = Column(String, nullable=True, default="")

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="profile")
