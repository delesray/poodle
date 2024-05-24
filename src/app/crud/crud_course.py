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
    filters = [Course.is_hidden == False]

    if tag:
        filters.append(Course.tags.any(Tag.name.like(f"%{tag}%")))
    if rating:
        filters.append(Course.rating >= rating)
    if name:
        filters.append(Course.title.like(f"%{name}%"))

    courses = db.query(Course).filter(*filters).order_by(Course.rating.desc()
                                                         ).offset((pages - 1) * items_per_page).limit(items_per_page).all()

    courses_list: List[CourseInfo] = []

    for course in courses:
        tags = await get_course_tags(course)
        response_model = CourseInfo.from_query(
            *(course.title, course.description, course.is_premium, tags))
        courses_list.append(response_model)
    return courses_list


async def get_course_tags(course: Course):
    return [tag.name for tag in course.tags]


async def get_course_by_id(db, course_id):
    course = db.query(Course).filter(Course.is_hidden == False, Course.id == course_id).first()

    return course

async def course_exists(db: Session, title: str):
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None
