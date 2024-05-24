from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from crud.crud_user import create, exists
from crud.crud_teacher import edit_account, get_teacher_by_id, get_info, get_my_courses
from crud.crud_course import course_exists, get_course_by_id
from schemas.teacher import TeacherEdit, TeacherCreate, TeacherResponseModel
from schemas.course import CourseCreate, CourseUpdate, CourseSectionsTags, CourseBase
from schemas.student import EnrollmentApproveRequest
from core.oauth import TeacherAuthDep
 

router = APIRouter(prefix='/teachers', tags=['teachers'])

@router.post("/register", status_code=201, response_model=TeacherResponseModel)
async def register_teacher(db: Annotated[Session, Depends(get_db)], user: TeacherCreate):
    """
    Registers a teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherCreate): The information of the teacher to register.

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
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Returns**: a TeacherResponseModel object with the teacher's account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """
    teacher = await get_teacher_by_id(db, user.account_id)
         
    return await get_info(teacher, user.email)


@router.put('/', status_code=200, response_model=TeacherResponseModel)
async def update_account(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep, updates: TeacherEdit):
    """
    Edits authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
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
    
    edited_teacher_account = await edit_account(db, teacher, updates)
    
    return await get_info(edited_teacher_account, user.email)


@router.post("/courses", status_code=201, response_model=CourseSectionsTags)
async def create_course(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep, course: CourseCreate):
    """
    Creates a new course for an authenticated teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `course` (CourseCreate): CourseCreate object that specifies the details of the new course.

    **Returns**: a CourseSectionsTags object with the details of the created course.

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


@router.get("/courses", response_model=list[CourseBase])
async def get_courses(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep): 
    """
    Returns teacher's courses.

    **Parameters:**
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Raises**:
    - HTTPException 401, if old password does not match.

    **Returns**: A list of CourseBase response models containing information about courses owned by the teacher.
    """
    
    teacher = await get_teacher_by_id(db, user.account_id)
    
    return await get_my_courses(db, teacher)


@router.get("/courses/{course_id}")
async def get_course_by_id(
    db: Annotated[Session, Depends(get_db)],
    course_id: int,
    user: TeacherAuthDep,
    sort: str | None = None,
    sort_by: str | None = None):
    
    if sort and sort.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort parameter"
        )

    if sort_by and sort_by.lower() not in ['section_id', 'title']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by parameter"
        )
        
    course = await get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail=f"Course #ID:{course_id} does not exist"
        )
    pass
    

@router.put("/courses/{course_id}")
async def update_course(course_id: int, existing_teacher: TeacherAuthDep, course_update: CourseUpdate = Body(...)):
    pass
#     if not course_update:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Data not provided to make changes")
# #add other validations        
#     return await edit_course(course_id, course_update)
   

@router.post("/approve-enrollment")
def approve_enrollment(request: EnrollmentApproveRequest, db: Annotated[Session, Depends(get_db)]):
    pass

@router.patch("/courses/{course_id}/deactivate")
def deactivate_course(course_id, existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
  pass

@router.get("/courses/reports")
def generate_course_reports(existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
    pass

  




