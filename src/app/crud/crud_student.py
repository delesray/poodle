from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.models import Account, Course, Student, StudentProgress
from schemas.student import StudentEdit, StudentResponseModel
from schemas.course import CourseInfo


async def get_by_email(db: Session, email: str):
    student = (db.query(Student).join(Student.account).filter(
        Account.email == email).first())

    if student:
        return student


async def get_student(db: Session, email: str):
    student = await get_by_email(db, email)

    if student:
        return StudentResponseModel(
            first_name=student.first_name,
            last_name=student.last_name,
            profile_picture=student.profile_picture,
            is_premium=student.is_premium,
            is_deactivated=student.is_deactivated
        )


async def edit_account(db: Session, email: str, updates: StudentEdit):
    student = await get_by_email(db, email)

    student.first_name, student.last_name, student.profile_picture = updates.first_name, \
        updates.last_name, updates.profile_picture

    db.commit()

    return StudentResponseModel(
        first_name=updates.first_name,
        last_name=updates.last_name,
        profile_picture=updates.profile_picture,
        is_premium=student.is_premium,
        is_deactivated=student.is_deactivated
    )


async def get_my_courses(student: Student):
    my_courses = student.courses_enrolled

    my_courses_pydantic: list[CourseInfo] = []
    for c in my_courses:
        tags = [str(t) for t in c.tags]
        my_courses_pydantic.append(CourseInfo.from_query(*(c.title, c.description, c.is_premium, tags)))

    return my_courses_pydantic


async def subscribe_for_course(db: Session, student: Student, course_id: int):

    new_enrollment = StudentProgress(
        student_id=student.student_id,
        course_id=course_id,
    )

    try:
        db.add(new_enrollment)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_enrollment)
        return new_enrollment


async def get_premium_courses_count(student):
    return len([course for course in student.courses_enrolled if course.is_premium])
