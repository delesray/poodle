from pydantic import BaseModel, StringConstraints
from typing import Annotated
from enum import Enum

class ContentType(str, Enum):
    video = 'video'
    image = 'image'
    text = 'text'
    quiz = 'quiz'

class SectionCreate(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)] 
    content: ContentType 
    description: Annotated[str, StringConstraints(min_length=1)] 
    external_link: Annotated[str, StringConstraints(min_length=1)] 
    course_id: int    
     
class SectionBase(BaseModel):
    pass
    