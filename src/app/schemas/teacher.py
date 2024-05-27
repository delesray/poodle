from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated


class TeacherEdit(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)]
    last_name: Annotated[str, StringConstraints(min_length=2)]
    phone_number: str | None = None
    linked_in: str | None = None


class TeacherCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=4)]
    first_name: Annotated[str, StringConstraints(min_length=2)]
    last_name: Annotated[str, StringConstraints(min_length=2)]
    phone_number: str | None = None
    linked_in: str | None = None
   
    def get_type(self):
        return 'teacher'


class TeacherSchema(BaseModel):
    teacher_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str = None
    linked_in: str = None
