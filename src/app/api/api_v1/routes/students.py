from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from crud import crud_course, crud_section
from core.oauth import StudentAuthDep
from api.api_v1.routes import utils
from crud import crud_user, crud_student
from schemas.course import CourseInfo, CourseRate, CourseRateResponse, StudentCourse
from schemas.section import SectionBase
from schemas.student import StudentCreate, StudentEdit, StudentResponseModel
from schemas.user import UserChangePassword
from database.database import get_db
from sqlalchemy.orm import Session
from database.models import Course

from fastapi import UploadFile


router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register', status_code=201, response_model=StudentResponseModel)
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

    return await crud_user.create(db=db, user_schema=student)


@router.post('/', status_code=201)
async def update_profile_picture(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, file: UploadFile):
    """
    Lets an authenticated student add or edit their profile picture.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentCreate): The information of the student to register.
    - `file` (BinaryIO): BinaryIO object containing the image data.

    **Returns**: Successful message, if the picture is uploaded.

    **Raises**: 
    - HTTPException 409, if a user with the same email has already been registered.
    - HTTPException 400, if the file is corruped or the student uploaded an unsupported media type.
    """
    if await crud_user.add_picture(db=db, picture=file, student_id=student.account_id):
        return 'Profile picture successfully uploaded!'
    raise HTTPException(
        status_code=400, detail='File is corrupted or media type is not supported')


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
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 401, if old password does not match.
    - HTTPException 400, if new password is the same as the old one.
    - HTTPException 400, if new password confirmation does not match.
    """

    await utils.change_pass_raise(account=student, pass_update=pass_update)

    await crud_user.change_password(db=db, pass_update=pass_update, account=student)


@router.get('/courses', response_model=list[CourseInfo])
async def view_my_courses(student: StudentAuthDep):
    """
    Returns authenticated student's courses.

    **Parameters:**
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.

    **Returns**: A list of CourseInfo response models with the information for each course the student is enrolled in.
    """
    my_courses = await crud_student.get_my_courses(student=student.student)
    return my_courses


@router.get('/courses/{course_id}', response_model=StudentCourse)
async def view_course(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, course_id: int):
    """
    Returns authenticated student's chosen course with details.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): The ID of the course the student wants to view.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 409, if the student is not enrolled in the course.

    **Returns**: A StudentCourse response object with detailed information about the course and the student's progress and rating of the course.
    """

    if not await crud_student.is_student_enrolled(student=student.student, course_id=course_id):
        raise HTTPException(
            status_code=409, detail='You have to enroll in this course to view details about it')

    return await crud_student.get_course_information(db=db, course_id=course_id, student=student.student)


@router.get('/courses/{course_id}/sections/{section_id}', response_model=SectionBase)
async def view_course_section(
        db: Annotated[Session, Depends(get_db)], student: StudentAuthDep,
        course_id: int, section_id: int
):
    """
    Returns authenticated student's chosen course section.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): The ID of the course the student wants to view.
    - `section_id` (integer): The ID of the section the student wants to view.

    **Returns**: SectionBase response object with information about the course section.

    **Raises**:
        - HTTPException 401, if the student is not authenticated.
        - HTTPException 404, if no such course or section.
        - HTTPException 403, if student is not enrolled in the course.

    """
    if not await crud_course.get_course_by_id(db, course_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such course'
        )

    section = await crud_section.get_section_by_id(db, section_id)
    if not section or not section.course_id == course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such Section'
        )

    if not await crud_student.is_student_enrolled(student=student.student, course_id=course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have to enroll in this course to view details about it'
        )

    await crud_section.add_student(db, section, student.account_id)
    section_dto = crud_section.transfer_object(section)
    return section_dto


@router.post('/courses/{course_id}/subscription', response_model=CourseInfo, status_code=201)
async def subscribe_for_course(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, course_id: int):
    """
    Enrolls authenticated student in a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): the ID of the course the student wants to enroll in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 403, if the student does not have a premium account but is attempting to enroll in a premium course.
    - HTTPException 400, if the student has reached their premium courses limit (5).
    - HTTPException 409, if the student is attempting to duplicate a course enrollment.


    **Returns**: CourseInfo object with home page information about the subscribed course.
    """

    course: Course = await crud_course.get_course_by_id(db=db, course_id=course_id)

    if course.is_premium and not student.student.is_premium:
        raise HTTPException(
            status_code=403, detail='Upgrade to premium to enroll in this course')

    if course.is_premium and await crud_student.get_premium_courses_count(student=student.student) >= 5:
        raise HTTPException(
            status_code=400, detail='Premium courses limit reached')

    return await crud_student.subscribe_for_course(db=db, student=student.student, course=course)


@router.delete('/courses/{course_id}/subscription', status_code=204)
async def unsubscribe(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, course_id: int):
    """
    Unsubscribes authenticated student from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): the ID of the course the student wants to enroll in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    """
    await crud_student.unsubscribe_from_course(db=db, student_id=student.account_id, course_id=course_id)


@router.patch('/courses/{course_id}/rating', status_code=201, response_model=CourseRateResponse)
async def rate_course(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, course_id: int,
                      rating: CourseRate):
    """
    Enables authenticated student to rate a course, if the student is enrolled in the course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): ID of the course to rate.
    - `rating` (CourseRate): rating the student wants to give.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 409, if the student is not enrolled in the course.
    - HTTPException 409, if the student is not enrolled in the course.
    - HTTPException 400, if the student has already rated the course.

    **Returns**: a CourseRateResponse object with the title of the course and the rating of the student.
    """

    if not await crud_student.is_student_enrolled(student=student.student, course_id=course_id):
        raise HTTPException(
            status_code=409, detail='You have to enroll in this course to rate it')

    if await crud_student.get_student_rating(db=db, student_id=student.account_id, course_id=course_id):
        raise HTTPException(
            status_code=400, detail='You have already rated this course')

    return await crud_student.add_student_rating(db=db, student=student.student, course_id=course_id,
                                                 rating=rating.rating)
