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
    content: ContentType 
    description: Annotated[str, StringConstraints(min_length=1)] | None = None 
    external_link: Annotated[str, StringConstraints(min_length=1)] | None = None
    course_id: int | None = None
    
    @classmethod
    def from_query(cls, section_id, title, content, description, external_link, course_id):
        return cls(
            section_id=section_id,
            title=title,
            content=content,
            description=description,
            external_link=external_link,
            course_id=course_id
        )
        
class SectionUpdate(BaseModel):
    pass

class SectionCreate(BaseModel):
    pass
    