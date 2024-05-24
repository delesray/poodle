from sqlalchemy.orm import Session
from database.models import Course, Tag
from schemas.course import CourseInfo
from typing import List



async def get_all_courses(
        db: Session,
        pages: int,
        items_per_page: int,
        tag: str = None,
        rating: int = None,
        name: str = None
):
    base_query = db.query(Course).filter(Course.is_hidden == False)

    filters = []
    if tag:
        filters.append(Course.tags.any(Tag.name.like(f"%{tag}%")))
    if rating:
        filters.append(Course.rating >= rating)
    if name:
        filters.append(Course.title.like(f"%{name}%"))

    if filters:
        base_query = base_query.filter(*filters)

    courses = base_query.order_by(Course.rating.desc()).offset((pages - 1) * items_per_page).limit(items_per_page).all()

    courses_list: List[CourseInfo] = []

    for course in courses:
        tags = await get_course_tags(course)
        pydantic_model = CourseInfo.from_query(*(course.title, course.description, course.is_premium, tags))
        courses_list.append(pydantic_model)
    return courses_list


async def get_course_tags(course):
    return [tag.name for tag in course.tags]


async def get_course_by_id(db, course_id):
    course = db.query(Course).filter(Course.is_hidden == False, Course.id == course_id).first()

    return course

async def course_exists(db: Session, title: str):
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None
