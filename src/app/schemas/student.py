from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints


class StudentCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=4)]
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None

    def get_type(self):
        return 'student'


class StudentResponseModel(BaseModel):
    first_name: str
    last_name: str
    is_premium: bool = False

    @classmethod
    def from_query(cls, first_name, last_name, is_premium=False):
        return cls(
            first_name=first_name,
            last_name=last_name,
            is_premium=is_premium
        )


class StudentEdit(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None


class StudentRatingSchema(BaseModel):
    student_id: int
    course_id: int
    rating: int
