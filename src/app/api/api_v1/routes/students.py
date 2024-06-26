from fastapi import APIRouter, HTTPException, status
from crud import crud_course, crud_section
from core.oauth import StudentAuthDep
from api.api_v1.routes import utils
from crud import crud_user, crud_student
from schemas.course import CourseInfo, CourseRate, CourseRateResponse, StudentCourseSchema
from schemas.section import SectionBase
from schemas.student import StudentCreate, StudentEdit, StudentResponseModel
from schemas.user import UserChangePassword
from db.models import Course
from fastapi import UploadFile
from db.database import dbDep

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=StudentResponseModel)
async def register_student(db: dbDep, student: StudentCreate) -> StudentResponseModel:
    """
    Registers a student.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentCreate): The information of the student to register.

    **Returns**: a StudentCreate object with the created student's details.

    **Raises**: HTTPException 409, if a user with the same email has already been registered.
    """
    if await crud_user.exists(db=db, email=student.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    return await crud_user.create(db=db, user_schema=student)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def update_profile_picture(db: dbDep, student: StudentAuthDep, file: UploadFile) -> str:
    """
    Lets an authenticated student add or edit their profile picture.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentCreate): The information of the student to register.
    - `file` (BinaryIO): BinaryIO object containing the image data.

    **Returns**: Successful message, if the picture is uploaded.

    **Raises**: 
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 400, if the file is corruped or the student uploaded an unsupported media type.
    """
    if await crud_user.add_picture(db=db, picture=file, entity_type='student', entity_id=student.student_id):
        return 'Profile picture successfully uploaded!'
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail='File is corrupted or media type is not supported')


@router.get('/', response_model=StudentResponseModel | None)
async def view_account(db: dbDep, student: StudentAuthDep) -> StudentResponseModel:
    """
    Shows authenticated student's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Returns**: a StudentResponseModel object with the student's account details.

    **Raises**: HTTPException 401, if the student is not authenticated.
    """
    return await crud_student.get_student(db=db, email=student.account.email)


@router.put('/', status_code=status.HTTP_201_CREATED, response_model=StudentResponseModel | None)
async def edit_account(db: dbDep, student: StudentAuthDep, updates: StudentEdit) -> StudentResponseModel:
    """
    Edits authenticated student's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `updates` (StudentEdit): StudentEdit object that specifies the desired account updates.

    **Returns**: a StudentResponseModel object with the student's edited account details.

    **Raises**: HTTPException 401, if the student is not authenticated.
    """
    return await crud_student.edit_account(db=db, email=student.account.email, updates=updates)


@router.patch('/', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: dbDep, student: StudentAuthDep,
                          pass_update: UserChangePassword) -> None:
    """
    Changes authenticated student's password.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `pass_update` (UserChangePassword): The form for changing student's password.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 401, if old password does not match.
    - HTTPException 400, if new password is the same as the old one.
    - HTTPException 400, if new password confirmation does not match.
    """
    await utils.change_pass_raise(account=student.account, pass_update=pass_update)

    await crud_user.change_password(db=db, pass_update=pass_update, account=student.account)


@router.get('/courses', response_model=list[CourseInfo])
async def view_my_courses(student: StudentAuthDep) -> list[CourseInfo]:
    """
    Returns authenticated student's courses.

    **Parameters:**
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Returns**: A list of CourseInfo response models with the information for each course the student is enrolled in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    """
    return await crud_student.get_my_courses(student=student)


@router.get('/courses/pending', response_model=list[CourseInfo] | None)
async def view_pending_courses(db: dbDep, student: StudentAuthDep) -> list[CourseInfo] | None:
    """
    Returns authenticated student's pending requests for courses.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.

    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    
    **Returns**: A list of CourseInfo response models with the information for each course the student has requested to enroll in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    """
    return await crud_student.view_pending_requests(db, student)


@router.get('/courses/{course_id}', response_model=StudentCourseSchema | None)
async def view_course(db: dbDep, student: StudentAuthDep, course_id: int) -> StudentCourseSchema:
    """
    Returns authenticated student's chosen course with details.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): The ID of the course the student wants to view.

    **Returns**: A StudentCourse response object with detailed information about the course and the student's progress and rating of the course.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 404, if the course is not found.
    - HTTPException 409, if the student is not enrolled in the course.
    """
    course: Course = await crud_course.get_course_by_id(db=db, course_id=course_id)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')

    if not await crud_student.is_student_enrolled(student=student, course_id=course_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='You have to enroll in this course to view details about it')

    return await crud_student.get_course_information(db=db, course_id=course_id, student=student)


@router.get('/courses/{course_id}/sections/{section_id}', response_model=SectionBase)
async def view_course_section(
        db: dbDep, student: StudentAuthDep,
        course_id: int, section_id: int
) -> SectionBase:
    """
    Returns authenticated student's chosen course section.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
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

    if not await crud_student.is_student_enrolled(student=student, course_id=course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have to enroll in this course to view details about it'
        )

    await crud_section.add_student(db, section, student.student_id)
    section_dto = crud_section.transfer_object(section)
    return section_dto


@router.post('/courses/{course_id}/subscription')
async def subscribe_for_course(db: dbDep, student: StudentAuthDep, course_id: int) -> str:
    """
    Sends a subscription request by email to the owner of the course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): the ID of the course the student wants to enroll in.

    **Returns**: 'Pending approval' message.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 404, if the course is not found.
    - HTTPException 403, if the student does not have a premium account but is attempting to enroll in a premium course.
    - HTTPException 400, if the student has reached their premium courses limit (5).
    - HTTPException 409, if the student is attempting to duplicate a course enrollment.
    """
    course: Course = await crud_course.get_course_by_id(db=db, course_id=course_id)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')

    if await crud_student.is_student_enrolled(student=student, course_id=course.course_id):
        return f'You are already subscribed for course {course.title}. Click on <View Course> or <View Course Section> to access its content'

    if course.is_premium and not student.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Upgrade to premium to enroll in this course')

    if course.is_premium and await crud_student.get_premium_courses_count(student=student) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Premium courses limit reached')

    return await crud_student.subscribe(db, course=course, student=student)


@router.delete('/courses/{course_id}/subscription', status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
        db: dbDep,
        student: StudentAuthDep,
        course_id: int) -> None:
    """
    Unsubscribes authenticated student from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): the ID of the course the student wants to enroll in.

    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    """
    course: Course = await crud_course.get_course_by_id(db=db, course_id=course_id)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')

    await crud_student.unsubscribe_from_course(db=db, student_id=student.student_id, course_id=course_id)


@router.post('/courses/{course_id}/rating', status_code=status.HTTP_201_CREATED, response_model=CourseRateResponse)
async def rate_course(db: dbDep, student: StudentAuthDep, course_id: int,
                      rating: CourseRate) -> CourseRateResponse:
    """
    Enables authenticated student to rate a course, if the student is enrolled in the course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.
    - `course_id` (integer): ID of the course to rate.
    - `rating` (CourseRate): rating the student wants to give.

    **Returns**: a CourseRateResponse object with the title of the course and the rating of the student.
    
    **Raises**:
    - HTTPException 401, if the student is not authenticated.
    - HTTPException 409, if the student is not enrolled in the course.
    """

    course: Course = await crud_course.get_course_by_id(db=db, course_id=course_id, auto_error=True)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')

    if not await crud_student.is_student_enrolled(student=student, course_id=course_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='You have to enroll in this course to rate it')

    return await crud_student.update_add_student_rating(
        db=db, student=student, course_id=course_id, rating=rating.rating)
