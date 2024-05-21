from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from core.oauth import StudentAuthDep
from crud import crud_user, crud_student
from schemas.student import StudentCreate
from database.database import DbSession, get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register', status_code=201)
async def register_student(db: DbSession, student: StudentCreate):
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


@router.get('/')
async def view_account(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
    """
    Shows student's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (StudentAuthDep): The authentication dependency for users with role Student.

    **Returns**: a StudentResponseModel object with the student's account details.

    **Raises**: HTTPException 401, if the student is not authenticated.

    """
    return await crud_student.get_student(db=db, email=student.email)
