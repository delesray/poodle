from pydantic import BaseModel, StringConstraints
from typing import Annotated

class Course(BaseModel):
    title: str
    description: str
    owner: int
    is_premium: bool
    home_page_picture: bytes
    rating: int


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
   