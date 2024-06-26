from pydantic import BaseModel, StringConstraints
from typing import Annotated
from enum import Enum


class ContentType(str, Enum):
    video = 'video'
    image = 'image'
    text = 'text'
    quiz = 'quiz'


class SectionBase(BaseModel):
    section_id: int | None = None
    title: Annotated[str, StringConstraints(min_length=1)]
    content_type: ContentType
    external_link: str | None = None
    description: str | None = None
    course_id: int | None = None

    @classmethod
    def from_query(cls, section_id, title, content_type, external_link, description, course_id):
        return cls(
            section_id=section_id,
            title=title,
            content_type=content_type,
            external_link=external_link,
            description=description,
            course_id=course_id
        )


class SectionUpdate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    content_type: ContentType
    external_link: str | None = None
    description: str | None = None
