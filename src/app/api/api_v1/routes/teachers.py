from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from crud.crud_user import create, exists
from crud.crud_teacher import update, create_new_course, get_teacher_by_id, get_info
from schemas.teacher import TeacherEditInfo, TeacherCreate
from schemas.course import Course, CourseUpdate
from schemas.student import EnrollmentApproveRequest
from core.oauth import TeacherAuthDep
 

router = APIRouter(prefix='/teachers', tags=['teachers'], responses={404: {"description": "Not found"}})

@router.post("/register")
async def register_teacher(db: Annotated[Session, Depends(get_db)], user: TeacherCreate):
    """
    Registers a teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherCreate): The information of the teacher to register.

    **Returns**: a TeacherResponseModel object with the created teacher's details.

    **Raises**: HTTPException 409, if a user with the same email has already been registered.

    """
    if await exists(db=db, email=user.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )
    new_teacher = create(db, user)   
    return await get_info(new_teacher, user.email)
    # return f"User with ID:{new_teacher.teacher_id} registered"

@router.get('/')
async def view_account(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep):
    """
    Shows authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Returns**: a TeacherResponseModel object with the teacher's account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """
    teacher =  get_teacher_by_id(db=db, id=user.account_id)
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="User is deactivated",
        )
        
    return await get_info(teacher, user.email)


@router.put('/')
async def update_info(teacher: TeacherEditInfo, existing_teacher: TeacherAuthDep):
    return await update(existing_teacher, teacher)


@router.post("/courses")
async def create_course(new_course: Course, existing_teacher: TeacherAuthDep):
    return await create_new_course(new_course, existing_teacher)

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

  




