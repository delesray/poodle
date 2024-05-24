from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from crud import crud_course
from database.models import Account, Course, Student, StudentProgress, StudentRating
from schemas.student import StudentEdit, StudentResponseModel
from schemas.course import CourseInfo, CourseRateResponse, StudentCourse


async def get_by_email(db: Session, email: str):
    student = (db.query(Student).join(Student.account).filter(
        Account.email == email).first())

    if student:
        return student


async def get_student(db: Session, email: str):
    student = await get_by_email(db, email)

    if student:
        return StudentResponseModel.from_query(student.first_name, student.last_name, student.profile_picture, student.is_premium)


async def edit_account(db: Session, email: str, updates: StudentEdit):
    student = await get_by_email(db, email)

    student.first_name, student.last_name, student.profile_picture = updates.first_name, \
        updates.last_name, updates.profile_picture

    db.commit()

    return StudentResponseModel.from_query(student.first_name, student.last_name, student.profile_picture, student.is_premium)


async def get_my_courses(student: Student):
    my_courses = student.courses_enrolled

    my_courses_pydantic: list[CourseInfo] = []
    for c in my_courses:
        tags = [str(t) for t in c.tags]
        my_courses_pydantic.append(CourseInfo.from_query(
            *(c.title, c.description, c.is_premium, tags)))

    return my_courses_pydantic


async def subscribe_for_course(db: Session, student: Student, course: Course):

    new_enrollment = StudentProgress(
        student_id=student.student_id,
        course_id=course.id,
    )

    try:
        db.add(new_enrollment)
        db.commit()

    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)

    else:
        db.refresh(new_enrollment)

        course_tags = await crud_course.get_course_tags(course)
        return CourseInfo(
            title=course.title,
            description=course.description,
            is_premium=course.is_premium,
            tags=course_tags)


async def unsubscribe_from_course(db: Session, student_id: int, course_id: int):
    db.query(StudentProgress).filter(StudentProgress.student_id ==
                                     student_id, StudentProgress.course_id == course_id).delete()
    db.commit()


async def is_student_enrolled(student: Student, course_id: int):
    return course_id in set([course.id for course in student.courses_enrolled])


async def get_premium_courses_count(student: Student):
    return len([course for course in student.courses_enrolled if course.is_premium])


async def get_student_rating(db: Session, student_id: int, course_id: int):
    query = db.query(StudentRating).filter(StudentRating.student_id ==
                                           student_id, StudentRating.course_id == course_id).first()

    if query:
        return query.rating


async def get_student_progress(db: Session, student_id: int, course_id: int):
    query = db.query(StudentProgress).filter(StudentProgress.student_id ==
                                             student_id, StudentProgress.course_id == course_id).first()

    if query:
        return query.progress


async def add_student_rating(db: Session, student: Student, course_id: int, rating: int):
    new_rating = StudentRating(
        student_id=student.student_id, course_id=course_id, rating=rating)

    db.add(new_rating)
    db.commit()

    course = next(
        (course for course in student.courses_enrolled if course.id == course_id), None)

    return CourseRateResponse(course=course.title,
                              rating=rating)


async def get_course_information(db: Session, course_id: int, student: Student):
    course: Course = await crud_course.get_course_common_info(db=db, course_id=course_id)
    student_rating = await get_student_rating(db=db, student_id=student.student_id, course_id=course_id)
    student_progress = await get_student_progress(db=db, student_id=student.student_id, course_id=course_id)

    if course:
        return StudentCourse(course_id=course.id,
                             title=course.title,
                             description=course.description,
                             objectives=course.objectives,
                             owner_id=course.owner_id,
                             owner_name=course.owner.first_name + ' ' + course.owner.last_name,
                             is_premium=course.is_premium,
                             home_page_picture=course.home_page_picture,
                             overall_rating=course.rating,
                             your_rating=student_rating if student_rating else 0,
                             your_progress=student_progress
                             )
