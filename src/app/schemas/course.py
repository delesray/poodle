from pydantic import BaseModel

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