from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from crud.crud_user import create, exists, check_deactivated
from crud.crud_teacher import edit_account, get_teacher_by_id, get_info
from crud.crud_course import make_course, course_exists
from schemas.teacher import TeacherEdit, TeacherCreate, TeacherResponseModel
from schemas.course import CourseCreate, CourseUpdate, CourseBase
from schemas.student import EnrollmentApproveRequest
from core.oauth import TeacherAuthDep
 

router = APIRouter(prefix='/teachers', tags=['teachers'], responses={404: {"description": "Not found"}})

@router.post("/register", status_code=201, response_model=TeacherResponseModel)
async def register_teacher(db: Annotated[Session, Depends(get_db)], user: TeacherCreate):
    """
    Registers a teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherCreate): The information of the teacher to register.

    **Returns**: a TeacherResponseModel object with the created teacher's details.

    **Raises**: HTTPException 409, if a user with the same email has already been registered.

    """
    if await exists(db, user.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )
    new_teacher = await create(db, user)   
    return await get_info(new_teacher, user.email)
    # return f"User with ID:{new_teacher.teacher_id} registered"

@router.get('/', response_model=TeacherResponseModel)
async def view_account(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep):
    """
    Shows authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Returns**: a TeacherResponseModel object with the teacher's account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """
    teacher = await get_teacher_by_id(db, user.account_id)
         
    return await get_info(teacher, user.email)


@router.put('/', status_code=200)
async def edit_account(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep, updates: TeacherEdit):
    """
    Edits authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `student` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (TeacherEdit): TeacherEdit object that specifies the desired account updates.

    **Returns**: a TeacherResponseModel object with the teacher's edited account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """
    if not updates:
        raise HTTPException(
            status_code=400,
            detail=f"Data not provided to make changes"
            )
        
    teacher = await get_teacher_by_id(db, user.account_id)
    
    return await edit_account(db, teacher, updates)


@router.post("/courses", status_code=201, response_model=CourseBase)
async def create_course(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep, course: CourseCreate):
    """
    Creates a new course for an authenticated teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `course` (CourseCreate): CourseCreate object that specifies the details of the new course.

    **Returns**: a CourseBase object with the details of the created course.

    **Raises**:
    - `HTTPException 409`: If a course with the same title already exists.
    - `HTTPException 401`: If the teacher is not authenticated.
    
    """
    if await course_exists(db, course.title):
        raise HTTPException(
            status_code=409,
            detail="Course with such title already exists",
        )
        
    teacher = await get_teacher_by_id(db, user.account_id)
     
    return await make_course(db, teacher, course)


@router.put("/courses/{course_id}")
async def update_course(course_id: int, existing_teacher: TeacherAuthDep, course_update: CourseUpdate = Body(...)):
    pass
#     if not course_update:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Data not provided to make changes")
# #add other validations        
#     return await edit_course(course_id, course_update)

@router.get("/courses/{course_id}")
async def get_course_by_id(course_id: int, existing_teacher: TeacherAuthDep):
    pass

@router.post("/approve-enrollment")
def approve_enrollment(request: EnrollmentApproveRequest, db: Annotated[Session, Depends(get_db)]):
    pass

@router.patch("/courses/{course_id}/deactivate")
def deactivate_course(course_id, existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
  pass

@router.get("/courses/reports")
def generate_course_reports(existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
    pass

  




