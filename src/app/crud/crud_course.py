from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from db.models import Course, Tag, StudentCourse
from schemas.course import CourseInfo
from typing import List


async def get_course_by_id(db: Session, course_id: int, auto_error=False) -> Course | None:
    query = db.query(Course).filter(Course.course_id == course_id).first()

    if query:
        return query
    if auto_error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')


async def get_course_by_id_or_raise_404(db, course_id):
    return await get_course_by_id(db, course_id, auto_error=True)


async def get_all_courses(
        db: Session,
        pages: int,
        items_per_page: int,
        tag: str = None,
        rating: float = None,
        name: str = None,
        teacher_id: int = None,
        student_id: int = None,
):
    filters = [Course.is_hidden == False]

    if tag:
        filters.append(Course.tags.any(Tag.name.like(f"%{tag}%")))
    if rating:
        filters.append(Course.rating >= rating)
    if name:
        filters.append(Course.title.like(f"%{name}%"))
    if teacher_id:
        filters.append(Course.owner_id == teacher_id)

    if student_id:
        filters.append(StudentCourse.student_id == student_id)
        courses = (db.query(Course).join(StudentCourse, StudentCourse.course_id == Course.course_id)
                   .filter(*filters).order_by(Course.rating.desc())
                   .offset((pages - 1) * items_per_page)
                   .limit(items_per_page).all())
    else:
        courses = (db.query(Course)
                   .filter(*filters).order_by(Course.rating.desc())
                   .offset((pages - 1) * items_per_page)
                   .limit(items_per_page).all())

    courses_list: List[CourseInfo] = []

    for course in courses:
        tags = await get_course_tags(course)
        response_model = CourseInfo.from_query(
            *(course.title, course.description, course.is_premium, tags))
        courses_list.append(response_model)
    return courses_list


async def get_course_tags(course: Course):
    return [tag.name for tag in course.tags]


async def get_course_common_info(db, course_id) -> Course | None:
    course = db.query(Course).filter(Course.is_hidden == False, Course.course_id == course_id).first()

    if course:
        return course


async def course_exists(db: Session, title: str) -> bool:
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None


async def update_rating(db: Session, course_id, new_st_rating, old_st_rating=None):
    # commit must happen in outer func

    # todo course_id > course (taken from dependency)
    course = db.query(Course).where(Course.course_id == course_id).first()

    if old_st_rating:  # means we do not increment people_rated
        course.rating = (course.rating * course.people_rated - old_st_rating + new_st_rating) / course.people_rated
        return

    if not course.rating:
        course.rating = new_st_rating
    else:
        course.rating = (course.rating * course.people_rated + new_st_rating) / (course.people_rated + 1)

    course.people_rated += 1


async def hide_course(db: Session, course: Course):
    course.is_hidden = True
    db.commit()
