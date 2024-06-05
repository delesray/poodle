from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.course import CourseInfo
from crud import crud_user, crud_course
from core.security import create_access_token, TokenData
from db.database import dbDep


router = APIRouter(tags=['public'])


@router.post('/login', include_in_schema=False)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: dbDep):
    """
    Logs a user.

    **Parameters:**
    - `form_data` (OAuth2PasswordRequestForm): the class dependency that implements the OAuth2 password flow
    - `db` (Session): The SQLAlchemy db session.

    **Returns**: a Token object (JWT)

    **Raises**: HTTPException 401, if the user's credentials are incorrect.

    """
    user = await crud_user.try_login(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await create_access_token(
        TokenData(email=user.email, role=user.role))
    return token


@router.get('/courses', response_model=list[CourseInfo])
async def get_courses(
        db: dbDep,
        tag: str | None = None,
        rating: float | None = None,
        name: str | None = None,
        pages: int = 1,
        items_per_page: int = 5
):
    """
    - Displays title, description and tags of all courses.
    - Courses can be searched by tag and/or rating.
    - Number of pages and items per page can also be specified.
    - By default, courses are ordered by rating in descending order.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `tag` (string): the course tags to filter by.
    - `rating` (integer): the minimum desired course rating to filter by.
    - `pages` (integer): the number of pages to be returned.
    - `items_per_page`: the number of items per page to be returned.

    **Returns**: a list of PublicCourseInfo models.
    """

    return await crud_course.get_all_courses(
        db=db, tag=tag, rating=rating, name=name, pages=pages, items_per_page=items_per_page
    )
