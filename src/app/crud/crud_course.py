from sqlalchemy.orm import Session
from database.models import Course, Tag, Teacher
from schemas.course import CourseCreate, CourseUpdate, CourseBase, CourseInfo
from typing import List


async def get_all_courses(
        db: Session,
        pages: int,
        items_per_page: int,
        tag: str = None,
        rating: int = None
):
    base_query = db.query(Course).filter(Course.is_hidden == False)

    filters = []
    if tag:
        filters.append(Course.tags.any(Tag.name.like(tag)))
    if rating:
        filters.append(Course.rating >= rating)

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


async def get_by_id(db, course_id):
    course = db.query(Course).filter(Course.is_hidden == False, Course.id == course_id).first()

    return course


async def get_courses(existing_teacher):
    # Teachers must be able to view their own courses
    pass


async def make_course(db: Session, teacher: Teacher, course: CourseCreate):
    new_course = Course(
        title=course.title,
        description=course.description,
        objectives=course.objectives,
        owner_id=teacher.teacher_id,
        is_premium=course.is_premium,
        is_hidden=False,
        home_page_picture=course.home_page_picture,
        rating=0
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return CourseBase(
        course_id=new_course.id,
        title=new_course.title,
        description=new_course.description,
        objectives=new_course.objectives,
        owner_id=new_course.owner_id,
        owner_names=teacher.first_name + ' ' + teacher.last_name,
        is_premium=new_course.is_premium,
        is_hidden=new_course.is_hidden,
        home_page_picture=new_course.home_page_picture,
        rating=new_course.rating
    )


async def edit_course(course_id, course_update):
    pass


async def course_exists(db: Session, title: str):
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None
