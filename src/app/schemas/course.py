from pydantic import BaseModel, StringConstraints
from typing import Annotated


class Course(BaseModel):
    title: str
    description: str
    owner: int
    is_premium: bool
    home_page_picture: bytes
    rating: int


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
    pass


class CourseCreate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] = None
    description: Annotated[str, StringConstraints(min_length=1)] = None
    objectives: Annotated[
        str, StringConstraints(min_length=1)] = None  # what students are expected to learn by the end of course
    is_premium: bool = False
    home_page_picture: bytes | None = None
