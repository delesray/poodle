from pydantic import BaseModel, EmailStr


class Student(BaseModel):
    pass


class EnrollmentApproveRequest(BaseModel):
    student_id: int
    course_id: int


class StudentCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    profile_picture: bytes | None = None

    def get_type(self):
        return 'student'


class StudentResponseModel(BaseModel):
    first_name: str
    last_name: str
    profile_picture: bytes | None = None
    is_premium: bool = False
    is_deactivated: bool = False
