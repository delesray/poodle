from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated
from schemas.section import SectionBase
from schemas.tag import TagBase

class CourseBase(BaseModel):
    course_id: int 
    title: str
    description: str
    objectives: str
    owner_id: int
    owner_names: str
    is_premium: bool = False
    is_hidden: bool = False
    home_page_picture: bytes = None
    rating: int = 0


class CourseInfo(BaseModel):
    title: str
    description: str
    is_premium: bool
    tags: list | None = []

    @classmethod
    def from_query(cls, title, description, is_premium, tags):
        return cls(
            title=title,
            description=description,
            is_premium=is_premium,
            tags=tags,
        )

class CourseUpdate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] #TODO discuss:  should title changes be limited?
    description: Annotated[str, StringConstraints(min_length=1)] 
    objectives: Annotated[str, StringConstraints(min_length=1)] 
    home_page_picture: bytes | None = None

class CourseCreate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] 
    description: Annotated[str, StringConstraints(min_length=1)] 
    objectives: Annotated[
        str, StringConstraints(min_length=1)]  # what students are expected to learn and accomplish by the end of the course
    is_premium: bool = False
    home_page_picture: bytes | None = None
    tags: list[TagBase]
    sections: list[SectionBase]
    
class CourseSectionsTags(BaseModel):
    course: CourseBase
    tags: list[TagBase]
    sections: list[SectionBase]
   

class CourseRate(BaseModel):
    rating: int = Field(default=10, ge=1, le=10)


class CourseRateResponse(BaseModel):
    course: str
    rating: int = Field(ge=1, le=10)


class StudentCourse(BaseModel):
    course_id: int 
    title: str
    description: str
    objectives: str
    owner_id: int
    owner_name: str
    is_premium: bool = False
    home_page_picture: bytes = None
    overall_rating: int = 0
    your_rating: int = 0
    your_progress: int = 0
