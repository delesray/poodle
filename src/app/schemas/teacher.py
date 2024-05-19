from pydantic import BaseModel
from sqlalchemy import LargeBinary

class Teacher(BaseModel):
    teacher_id: int | None = None
    first_name: str
    last_name: str
    phone_number: str | None = None
    linkedin: str | None = None
    profile_picture: LargeBinary | None = None
    is_deactivated: bool | None = None
    
    

class TeacherEditInfo(BaseModel):
    phone_number: str | None = None
    linkedin: str | None = None
    profile_picture: LargeBinary | None = None
    
    
    
    
