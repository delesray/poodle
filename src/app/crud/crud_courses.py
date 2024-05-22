from sqlalchemy.orm import Session
from database.models import Course, Tag
from schemas.course import PublicCourseInfo
from typing import List


async def get_all_public_courses(db: Session,
                                 pages: int,
                                 items_per_page: int,
                                 tag: str = None,
                                 rating: int = None
                                 ):

    base_query = db.query(Course) \
        .filter(Course.is_premium == False, Course.is_hidden == False)

    if tag:
        base_query = base_query.filter(Course.tags.any(Tag.name.like(tag)))

    if rating:
        base_query = base_query.filter(Course.rating >= rating)

    courses = base_query.order_by(Course.rating.desc()).offset((pages - 1) * items_per_page).limit(items_per_page).all()
    courses_list: List[PublicCourseInfo] = []

    for course in courses:
        tags = [tag.name for tag in course.tags]
        pydantic_model = PublicCourseInfo(title=course.title,
                                        description=course.description,
                                        tags=tags)
        courses_list.append(pydantic_model)
        
    return courses_list
