from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from crud import crud_course
from core.oauth import StudentAuthDep
from api.api_v1.routes import utils
from crud import crud_user, crud_student
from schemas.course import CourseInfo
from schemas.student import StudentCreate, StudentEdit, StudentResponseModel
from schemas.user import UserChangePassword
from database.database import get_db
from sqlalchemy.orm import Session
from database.models import Course, Student, StudentProgress

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register', status_code=201, response_model=StudentCreate)
async def register_student(db: Annotated[Session, Depends(get_db)], student: StudentCreate):
    """
    Registers a student.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentCreate): The information of the student to register.

    **Returns**: a StudentCreate object with the created student's details.

    **Raises**: HTTPException 409, if a user with the same email has already been registered.

    """
    if await crud_user.exists(db=db, email=student.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    return await crud_user.create(db, student)


@router.get('/', response_model=StudentResponseModel)
async def view_account(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
    """
    Shows authenticated student's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Returns**: a StudentResponseModel object with the student's account details.

    **Raises**: HTTPException 401, if the student is not authenticated.

    """
    return await crud_student.get_student(db=db, email=student.email)


@router.put('/', status_code=201, response_model=StudentResponseModel)
async def edit_account(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, updates: StudentEdit):
    """
    Edits authenticated student's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `updates` (StudentEdit): StudentEdit object that specifies the desired account updates.

    **Returns**: a StudentResponseModel object with the student's edited account details.

    **Raises**: HTTPException 401, if the student is not authenticated.

    """
    return await crud_student.edit_account(db=db, email=student.email, updates=updates)


@router.patch('/', status_code=204)
async def change_password(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep,
                          pass_update: UserChangePassword):
    """
    Changes authenticated student's password.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `pass_update` (UserChangePassword):

    **Raises**:
    - HTTPException 401, if old password does not match.
    - HTTPException 400, if new password is the same as the old one.
    - HTTPException 400, if new password confirmation does not match.

    """

    await utils.change_pass_raise(student, pass_update)

    await crud_user.change_password(db, pass_update, student)


@router.get('/mycourses', response_model=list[CourseInfo])
async def view_my_courses(student: StudentAuthDep):
    """
    Returns student's courses.

    **Parameters:**
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Raises**:
    - HTTPException 401, if old password does not match.

    **Returns**: A list of CourseInfo response models with the information for each course the student is enrolled in.
    """
    my_courses = await crud_student.get_my_courses(student.student)
    return my_courses


# @router.get('/')
# async def get_course_progress(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
#
#     **Parameters:**
#
#     **Returns**:
#
#     **Raises**:
#
#     """
#     pass


# @router.get('/')
# async def get_enrolled_courses(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
#     TODO seacrh by name | tag

#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass


# @router.put('/')
# async def get_premium_tier(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
#     TODO discuss?
#     set expiration?
#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass


@router.post('/courses/{course_id}/subscription')
async def subscribe_for_course(
        course_id: int,
        db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
    """
    Enrolls student in a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): the ID of the course the student wants to enroll in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 403, if the student does not have a premium account but is attempting to enroll in a premium course.
    - HTTPException 400, if the student has reached their premium courses limit (5).
    - HTTPException 409, if the student is attempting to duplicate a course enrollment.

    TODO return object?
    **Returns**: Successful message, if the student is enrolled in the course.

    """

    course: Course = await crud_course.get_by_id(db, course_id)

    if course.is_premium and not student.student.is_premium:
        raise HTTPException(status_code=403, detail='Upgrade to premium to enroll in this course')
    
    if await crud_student.get_premium_courses_count(student.student) >= 5:
        raise HTTPException(status_code=400, detail='Premium courses limit reached')
    
    await crud_student.subscribe_for_course(db, student.student, course_id)
    return f'Subscription for course {course_id} successful!'


# @router.put('/')
# async def unsubscribe(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """

#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass


# @router.put('/')
# async def rate_course(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """

#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass
