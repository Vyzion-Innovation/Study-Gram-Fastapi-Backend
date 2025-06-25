from pydantic import BaseModel
from typing import List
from datetime import date

# Schema for submitting attendance
class TeacherAttendanceCreate(BaseModel):
    teacher_ids: List[int]
    target_date: date

# Schema for returning teacher data
class TeacherBase(BaseModel):
    id: int
    name: str
    contact_number: str

    class Config:
        orm_mode = True

# Schema for response
class TeacherAttendanceResponse(BaseModel):
    data: List[TeacherBase]

