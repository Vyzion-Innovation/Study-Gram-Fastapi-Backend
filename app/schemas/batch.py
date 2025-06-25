from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import Form

# ===============================
# Batch
# ===============================

class BatchBase(BaseModel):
    name: str
    description: Optional[str] = None

class BatchCreate(BatchBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: Optional[str] = Form(None)
    ):
        return cls(name=name, description=description)

class BatchUpdate(BatchBase):
    pass

class BatchOut(BatchBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===============================
# Course
# ===============================

class CourseBase(BaseModel):
    course_name: str

class CourseCreate(CourseBase):
    @classmethod
    def as_form(cls, course_name: str = Form(...)):
        return cls(course_name=course_name)

class CourseOut(CourseBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===============================
# Payment Duration
# ===============================

class DurationBase(BaseModel):
    duration_time: str

class DurationCreate(DurationBase):
    @classmethod
    def as_form(cls, duration_time: str = Form(...)):
        return cls(duration_time=duration_time)

class DurationOut(DurationBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
