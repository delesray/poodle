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

    filters = []
    if tag:
        filters.append(Course.tags.any(Tag.name.like(tag)))
    if rating:
        filters.append(Course.rating >= rating)

    if filters:
        base_query = base_query.filter(*filters)

    courses = base_query.order_by(Course.rating.desc()).offset((pages - 1) * items_per_page).limit(items_per_page).all()

    courses_list: List[PublicCourseInfo] = []

    for course in courses:
        tags = [tag.name for tag in course.tags]
        pydantic_model = PublicCourseInfo(title=course.title,
                                        description=course.description,
                                        tags=tags)
        courses_list.append(pydantic_model)
        
    return courses_list


async def get_by_id(course_id):
    #Teachers must be able to view their own courses
    pass

async def get_courses(existing_teacher):
    #Teachers must be able to view their own courses
    pass

async def create_course(new_course, existing_teacher):
    pass

async def edit_course(course_id, course_update):
    pass

async def get_all_courses(
    #Admins could be able to view a list with all public and premium courses, the number of students in them and their rating
        page: int,
        size: int,
        search: str = None,
        owner_id: int = None,
        student_id: int = None
        ):
    pass
