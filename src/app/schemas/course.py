from pydantic import BaseModel, StringConstraints
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
    title: str #TODO discuss:  should title changes be limited?
    description: str
    objectives: str
    home_page_picture: bytes = None

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
   

    
    
