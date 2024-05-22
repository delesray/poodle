from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated

class TeacherBase(BaseModel):
    teacher_id: int | None = None
    first_name: str
    last_name: str
    phone_number: str | None = None
    linked_in: str | None = None
    profile_picture: bytes | None = None
    is_deactivated: bool | None = None
    
    

class TeacherEdit(BaseModel):
    first_name: Annotated[str, StringConstraints(min_length=2)] = None
    last_name: Annotated[str, StringConstraints(min_length=2)] = None
    phone_number: str | None = None
    linked_in: str | None = None
    profile_picture: bytes | None = None


class TeacherCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    linked_in: str | None = None
    profile_picture: bytes | None = None

    def get_type(self):
        return 'teacher'
    
class TeacherResponseModel(BaseModel):
    teacher_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str 
    linked_in: str 
    profile_picture: bytes 
    
    
    
    
    
    
    
