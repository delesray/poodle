from fastapi import APIRouter, HTTPException
from crud.crud_user import create, exists
from schemas.student import StudentCreate
from database.database import DbSession


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
    if await exists(db=db, email=student.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    return await create(db, student)
