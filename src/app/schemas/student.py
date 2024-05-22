from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints


class Student(BaseModel):
    pass


class EnrollmentApproveRequest(BaseModel):
    student_id: int
    course_id: int


class StudentCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=4)] = None
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None
    profile_picture: bytes | None = None

    def get_type(self):
        return 'student'


class StudentResponseModel(BaseModel):
    first_name: str
    last_name: str
    profile_picture: bytes | None = None
    is_premium: bool = False


class StudentEdit(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None
    profile_picture: bytes | None = None
