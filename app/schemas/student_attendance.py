from pydantic import BaseModel
from typing import List
from datetime import date

class StudentAttendanceCreate(BaseModel):
    batch_id: int
    date: date
    present_student_ids: List[int]

class StudentAttendanceUpdate(StudentAttendanceCreate):
    pass

class StudentAttendanceOut(BaseModel):
    id: int
    batch_id: int
    date: date
    present_student_ids: List[int]

    class Config:
        orm_mode = True
