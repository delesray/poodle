from pydantic import BaseModel, StringConstraints
from typing import Annotated

class CourseBase(BaseModel):
    course_id: int
    title: str
    description: str
    objectives: str
    owner_id: int
    is_premium: bool = False
    is_hidden: bool = False
    home_page_picture: bytes = None
    rating: int = 0
       
class PublicCourseInfo(BaseModel):
    title: str
    description: str
    tags: list | None = []

class CourseUpdate(BaseModel):
    pass

class CourseCreate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] = None
    description: Annotated[str, StringConstraints(min_length=1)] = None
    objectives: Annotated[str, StringConstraints(min_length=1)] = None # what students are expected to learn by the end of course
    is_premium: bool = False
    home_page_picture: bytes | None = None
   