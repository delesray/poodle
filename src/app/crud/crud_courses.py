from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from database.models import Course
from schemas.course import Course as PydanticCourse
from typing import List


async def get_all_public_courses(db: Session,
                                 pages: int,
                                 items_per_page: int,
                                 title: str = None,
                                 rating: int = None
                                 ):

    base_query = db.query(Course) \
        .filter(Course.is_premium == False, Course.is_hidden == False)

    if title:
        base_query = base_query.filter(Course.title.like(title))

    if rating:
        base_query = base_query.filter(Course.rating >= rating)

    courses = base_query.order_by(Course.rating.desc()).offset((pages - 1) * items_per_page).limit(items_per_page).all()
    courses_pydantic: List[PydanticCourse] = []

    for course in courses:
        pydantic_model = PydanticCourse(title=course.title,
                                        description=course.description,
                                        owner=course.owner_id,
                                        is_premium=course.is_premium,
                                        home_page_picture=course.home_page_picture,
                                        rating=course.rating)
        courses_pydantic.append(pydantic_model)
        
    return courses_pydantic
