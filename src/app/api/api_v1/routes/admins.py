from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Not found"}},
)


@router.get('/courses')
async def get_courses(
        db: Annotated[Session, Depends(get_db)],
        tag: str | None = None,
        rating: int | None = None,
        name: str | None = None,
        pages: int = 1,
        items_per_page: int = 5
):
    """
    Enables an admin to view all courses, the number of students in them and their rating.
    Admins can search through courses by teacher/student.
    Pagination is also supported.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `tag` (string): the course tags to filter by.
    - `rating` (integer): the minimum desired course rating to filter by.
    - `pages` (integer): the number of pages to be returned.
    - `items_per_page`: the number of items per page to be returned.

    **Returns**: a list of AdminCourseInfo models.
    """

    pass


@router.patch('/accounts/{account_id}')
async def switch_account_activation(
        db: Annotated[Session, Depends(get_db)],
        tag: str | None = None,
        rating: int | None = None,
        name: str | None = None,
        pages: int = 1,
        items_per_page: int = 5
):
    pass


@router.get('/courses/{course_id}')
async def get_course_rating_info():
    pass


@router.put('/accounts/{student_id}')
async def make_student_premium():
    pass


@router.post('/accounts/{student_id}')
async def approve_teacher_registration():
    pass


@router.delete('/courses/{course_id}')
async def hide_course():
    pass


@router.delete('/courses/{course_id}/students/{student_id}')
async def remove_student_from_course():
    pass
