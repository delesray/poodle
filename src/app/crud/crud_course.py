from sqlalchemy.orm import Session
from database.models import Course, Tag, Teacher
from schemas.course import CourseCreate, CourseUpdate, CourseBase, CourseInfo, CourseSectionsTags
from typing import List
from crud.crud_section import create_sections
from crud.crud_tag import create_tags


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


async def get_courses(existing_teacher):
    # Teachers must be able to view their own courses
    pass


async def make_course(db: Session, teacher: Teacher, new_course: CourseCreate):
    course_info = Course(
        title=new_course.title,
        description=new_course.description,
        objectives=new_course.objectives,
        owner_id=teacher.teacher_id,
        is_premium=new_course.is_premium,
        is_hidden=False,
        home_page_picture=new_course.home_page_picture,
        rating=0
    )

    db.add(course_info)
    db.commit()
    db.refresh(course_info)
    course_info_response = CourseBase(
        course_id=course_info.id,
        title=course_info.title,
        description=course_info.description,
        objectives=course_info.objectives,
        owner_id=course_info.owner_id,
        owner_names=teacher.first_name + ' ' + teacher.last_name,
        is_premium=course_info.is_premium,
        is_hidden=course_info.is_hidden,
        home_page_picture=course_info.home_page_picture,
        rating=course_info.rating
    )
    course_tags = await create_tags(db, new_course.tags, course_info.id)
    course_sections = await create_sections(db, new_course.sections, course_info.id)
    
    return CourseSectionsTags(
        course=course_info_response,
        tags=course_tags,
        sections=course_sections
    )


async def edit_course(course_id, course_update):
    pass


async def course_exists(db: Session, title: str):
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None
