from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from core.oauth import StudentAuthDep
from app.api.api_v1.routes import utils
from crud import crud_user, crud_student
from schemas.student import StudentCreate, StudentEdit, StudentResponseModel
from schemas.user import UserChangePassword
from database.database import get_db
from sqlalchemy.orm import Session


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
async def change_password(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep, pass_update: UserChangePassword):
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


# @router.get('/')
# async def view_courses(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
#     TODO seacrh by name | tag
    
#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass


# @router.get('/')
# async def get_course_progress(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
    
#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

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


# @router.put('/')
# async def subscribe(db: Annotated[Session, Depends(get_db)], student: StudentAuthDep):
#     """
#     TODO max 5 premium
#     **Parameters:**

#     **Returns**: 

#     **Raises**: 

#     """
#     pass


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
