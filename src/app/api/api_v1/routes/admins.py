from fastapi import APIRouter, HTTPException, status
from crud import crud_course, crud_admin, crud_user
from core.oauth import AdminAuthDep
from crud.crud_user import Role
from db.database import dbDep

router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Not found"}},
)


@router.get('/courses')
async def get_courses(
        db: dbDep, admin: AdminAuthDep,
        tag: str | None = None,
        rating: int | None = None,
        name: str | None = None,
        pages: int = 1,
        items_per_page: int = 5,
):
    """
    Enables an admin to view all courses, the number of students in them and their rating.
    Admins can search through courses by teacher/student.
    Pagination is also supported.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `tag` (string): the course tags to filter by.
    - `rating` (integer): the minimum desired course rating to filter by.
    - `pages` (integer): the number of pages to be returned.
    - `items_per_page`: the number of items per page to be returned.

    **Returns**: a list of AdminCourseInfo models.
    """

    # todo ?
    return await crud_course.get_all_courses(
        db=db, tag=tag, rating=rating, name=name, pages=pages, items_per_page=items_per_page
    )


@router.patch('/accounts/{account_id}')
async def switch_user_activation(
        db: dbDep, admin: AdminAuthDep, account_id: int,
):
    user = await crud_user.get_user_by_id_deactivated_also(db, account_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such user')
    if admin.admin_id == user.account.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'You cannot deactivate yourself')

    await crud_admin.switch_user_activation(db, user)


@router.get('/courses/{course_id}')
async def get_course_rating_info(
        db: dbDep, admin: AdminAuthDep, course_id: int,
):
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    students_courses_rating = await crud_admin.get_students_ratings_by_course_id(db, course.course_id)

    # todo discuss
    return [course, students_courses_rating]


@router.patch('/students/{student_id}')
async def make_student_premium(
        db: dbDep, admin: AdminAuthDep, student_id: int,
):
    student = await crud_user.get_specific_user_or_raise_404(db, student_id, role=Role.STUDENT)
    await crud_admin.make_student_premium(db, student)


@router.post('/teachers/{teacher_id}')
async def approve_teacher_registration(
        db: dbDep, admin: AdminAuthDep, teacher_id: int,
):
    # todo Admins could approve registrations for teachers (via email).
    teacher = await crud_user.get_specific_user_or_raise_404(db, teacher_id, role=Role.TEACHER)
    await crud_admin.approve_teacher_registration(db, teacher)


@router.delete('/courses/{course_id}')
async def hide_course(
        db: dbDep, admin: AdminAuthDep, course_id: int,
):
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    await crud_admin.hide_course(db, course)


@router.delete('/courses/{course_id}/students/{student_id}')
async def remove_student_from_course(
        db: dbDep, admin: AdminAuthDep, course_id: int, student_id: int
):
    course = await crud_course.get_course_by_id_or_raise_404(db, course_id)
    student = await crud_user.get_specific_user_or_raise_404(db, student_id, role=Role.STUDENT)

    # todo test if it is already deleted what happens
    await crud_admin.remove_student_from_course(db, student.student_id, course.course_id)
