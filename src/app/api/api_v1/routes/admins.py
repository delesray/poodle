from fastapi import APIRouter, HTTPException, status
from schemas.course import CourseInfo, CourseStudentRatingsSchema
from schemas.student import StudentRatingSchema
from crud import crud_course, crud_admin, crud_user, crud_teacher
from core.oauth import AdminAuthDep
from crud.crud_user import Role
from db.database import dbDep

router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Not found"}},
)


@router.get('/courses', response_model=list[CourseInfo])
async def get_courses(
        db: dbDep, 
        admin: AdminAuthDep,
        pages: int = 1,
        items_per_page: int = 5,
        tag: str | None = None,
        rating: float | None = None,
        name: str | None = None,
        teacher_id: int | None = None,
        student_id: int | None = None,
):
    """
    Enables an admin to view all courses, the number of students in them and their rating.
    Admins can search through courses by teacher/student.
    Pagination is also supported.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `pages` (integer): The number of pages to be returned.
    - `items_per_page`: The number of items per page to be returned.
    - `tag` (string): The course tags to filter by.
    - `rating` (integer): The minimum desired course rating to filter by.
    - `name` (string): The title of the course to search by.
    - `student_id` (integer): The ID of the student to filter by.
    - `teacher_id` (integer): The ID of the teacher to filter by.

    **Returns**: a list of CourseInfo models.
    """

    return await crud_course.get_all_courses(
        db=db, tag=tag, rating=rating, name=name, pages=pages, items_per_page=items_per_page,
        teacher_id=teacher_id, student_id=student_id
    )


@router.patch('/accounts/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
async def switch_user_activation(
        db: dbDep, admin: AdminAuthDep, account_id: int,
):
    """
    Activates or deactivates a user account.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `account_id` (integer): The account ID of the user.

    **Raises**:
    - HTTPException 404, if no such account exists.
    - HTTPException 409, if admin tries to deactivate himself.
    """

    user = await crud_user.get_user_by_id_deactivated_also(db, account_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such user')
    if admin.admin_id == user.account_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'You cannot deactivate yourself')

    await crud_admin.switch_user_activation(db, user)


@router.get('/courses/{course_id}')
async def get_course_rating_info(
        db: dbDep, admin: AdminAuthDep, course_id: int,
):
    """
    Gets course rating info

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `course_id` (integer): The ID of the course to check the rating for.

    **Raises**:
    - HTTPException 404, if no such course.

    **Returns**: CourseStudentRatingsSchema containing the course and students who have rated it.
    """
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    students_courses_rating = await crud_admin.get_students_ratings_by_course_id(db, course.course_id)
    
    teacher = await crud_user.get_specific_user_or_raise_404(db, course.owner_id, Role.TEACHER)
    course_base = crud_teacher.get_coursebase_model(teacher, course)

    ratings = [StudentRatingSchema(student_id=studrating.student_id, course_id=studrating.course_id, rating=studrating.rating)
               for studrating in students_courses_rating]

    return CourseStudentRatingsSchema(course=course_base, ratings=ratings)
   

@router.patch('/students/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
async def make_student_premium(
        db: dbDep, admin: AdminAuthDep, student_id: int,
):
    """
    Makes a student account premium.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `student_id` (integer): The ID of the student's account.

    **Raises**:
    - HTTPException 404, if no such user.
    """

    student = await crud_user.get_specific_user_or_raise_404(db, student_id, role=Role.STUDENT)
    await crud_admin.make_student_premium(db, student)


@router.delete('/courses/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def hide_course(
        db: dbDep, admin: AdminAuthDep, course_id: int,
):
    """
    Hides a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `course_id` (integer): The ID of the course to hide.

    **Raises**:
    - HTTPException 404, if no such course.
    """
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    await crud_admin.hide_course(db, course)


@router.delete('/courses/{course_id}/students/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_student_from_course(
        db: dbDep, admin: AdminAuthDep, course_id: int, student_id: int
):
    """
    Removes a student from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `admin` (AdminAuthDep): The authentication dependency for users with role Admin.
    - `student_id` (integer): The ID of the student to remove.
    - `course_id` (integer): The ID of the course to remove.

    **Raises**:
    - HTTPException 404, if no such user or course or the student is not enrolled in the course.
    """
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    student = await crud_user.get_specific_user_or_raise_404(db, student_id, role=Role.STUDENT)

    if not await crud_admin.remove_student_from_course(db, student.student_id, course.course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student is not enrolled in this course")
