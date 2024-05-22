from pydantic import BaseModel

class Course(BaseModel):
    title: str
    description: str
    owner: int
    is_premium: bool
    home_page_picture: bytes
    rating: int


class CourseUpdate(BaseModel):
    pass