from pydantic import BaseModel

class Student(BaseModel):
    pass

class EnrollmentApproveRequest(BaseModel):
    student_id: int
    course_id: int