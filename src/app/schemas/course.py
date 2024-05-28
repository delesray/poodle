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
    rating: float | None = None
    people_rated: int = 0


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
    title: Annotated[str, StringConstraints(min_length=1)] 
    description: Annotated[str, StringConstraints(min_length=1)] 
    objectives: Annotated[str, StringConstraints(min_length=1)] 


class CourseCreate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: Annotated[str, StringConstraints(min_length=1)]
    objectives: Annotated[  # what students are expected to learn and accomplish by the end of the course
        str, StringConstraints(min_length=1)]
    is_premium: bool = False
    tags: list[TagBase] | None = None
    sections: list[SectionBase] | None = None


class CourseSectionsTags(BaseModel):
    course: CourseBase
    tags: list[TagBase]
    sections: list[SectionBase]


class CourseRate(BaseModel):
    rating: int = Field(default=10, ge=1, le=10)


class CourseRateResponse(BaseModel):
    course: str
    rating: float = Field(ge=1, le=10)


class StudentCourse(BaseModel):
    course_id: int
    title: str
    description: str
    objectives: str
    owner_id: int
    owner_name: str
    is_premium: bool = False
    overall_rating: float | None = 0
    your_rating: float | None = 0
    your_progress: float | None  = 0


class CoursePendingRequests(BaseModel):
    course: str
    requested_by: str

    @classmethod
    def from_query(cls, course, requested_by):
        return cls(
            course=course,
            requested_by=requested_by
        )
