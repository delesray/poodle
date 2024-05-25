from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from crud.crud_user import create, exists
from crud import crud_teacher
from crud.crud_course import course_exists, get_course_common_info
from schemas.teacher import TeacherEdit, TeacherCreate, TeacherResponseModel
from schemas.course import CourseCreate, CourseUpdate, CourseSectionsTags, CourseBase
from schemas.student import EnrollmentApproveRequest
from schemas.section import SectionUpdate, SectionCreate
from schemas.tag import TagBase
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
    return await crud_teacher.get_info(new_teacher, user.email)
   

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
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)
         
    return await crud_teacher.get_info(teacher, user.email)


@router.put('/', status_code=200, response_model=TeacherResponseModel)
async def update_account(
    db: Annotated[Session, Depends(get_db)],
    user: TeacherAuthDep,
    updates: TeacherEdit = Body(...)
    ):
    """
    Edits authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (TeacherEdit): TeacherEdit object that specifies the desired account updates.

    **Returns**: a TeacherResponseModel object with the teacher's edited account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """
    # if not updates:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Data not provided to make changes"
    #         )
        
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)
    
    edited_teacher_account = await crud_teacher.edit_account(db, teacher, updates)
    
    return await crud_teacher.get_info(edited_teacher_account, user.email)


@router.post("/courses", status_code=201, response_model=CourseSectionsTags)
async def create_course(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep, course: CourseCreate):
    """
    Creates a new course for an authenticated teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `course` (CourseCreate): CourseCreate object that specifies the details of the new course.

    **Returns**: a CourseSectionsTags object with the details, tags, and sections of the created course.

    **Raises**:
    - `HTTPException 409`: If a course with the same title already exists.
    - `HTTPException 401`: If the teacher is not authenticated.
    
    """
    if await course_exists(db, course.title):
        raise HTTPException(
            status_code=409,
            detail="Course with such title already exists",
        )
        
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)
     
    return await crud_teacher.make_course(db, teacher, course)


@router.get("/courses", response_model=list[CourseBase])
async def get_courses(db: Annotated[Session, Depends(get_db)], user: TeacherAuthDep): 
    """
    Returns teacher's courses.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Raises**:
    - HTTPException 401, If the teacher is not authenticated.

    **Returns**: A list of CourseBase response models containing information about courses owned by the teacher.
    """
    
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)
    
    return await crud_teacher.get_my_courses(db, teacher)


@router.get("/courses/{course_id}", response_model=CourseSectionsTags)
async def view_course_by_id(
    db: Annotated[Session, Depends(get_db)],
    course_id: int,
    user: TeacherAuthDep,
    sort: str | None = None,
    sort_by: str | None = None
    ):
    
    """
    Retrieves a course by its ID along with associated tags and sections.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course to retrieve.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `sort` (str, optional): Sort order, either 'asc' or 'desc'.
    - `sort_by` (str, optional): Field to sort by, either 'section_id' or 'title'.
    
    **Returns**: A `CourseSectionsTags` object containing the course details, tags, and sections.

    **Raises**:
    - `HTTPException 400`: If the sort or sort_by parameters are invalid.
    - `HTTPException 404`: If the course with the given ID does not exist.
    - `HTTPException 403`: If the authenticated teacher does not have permission to access the course.
    """
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
        
    course = await get_course_common_info(db, course_id)    
    user_has_access, msg = crud_teacher.validate_course_access(course, user)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
        
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)
    
    return await crud_teacher.get_entire_course(db=db, course=course, teacher=teacher, sort=sort, sort_by=sort_by)
    

@router.put("/courses/{course_id}", status_code=200, response_model=CourseBase)
async def update_course_info(
    db: Annotated[Session, Depends(get_db)],
    course_id: int,
    user: TeacherAuthDep,
    updates: CourseUpdate = Body(...)
    ):
    
    course = await get_course_common_info(db, course_id)    
    user_has_access, msg = crud_teacher.validate_course_access(course, user)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
        
    teacher = await crud_teacher.get_teacher_by_id(db, user.account_id)       
    return await crud_teacher.edit_course_info(db, course, teacher, updates)


@router.put("/courses/{course_id}/sections/{section_id}")
async def update_section(db: Annotated[Session, Depends(get_db)], course_id: int, section_id: int, user: TeacherAuthDep, updates: SectionUpdate = Body(...)):
    pass  

@router.post("/courses/{course_id}/sections")
async def add_section(db: Annotated[Session, Depends(get_db)], course_id: int, user: TeacherAuthDep, section: SectionCreate):
    pass 

@router.delete("/courses/{course_id}/sections/{section_id}")
async def remove_section(db: Annotated[Session, Depends(get_db)], course_id: int, section_id: int, user: TeacherAuthDep):
    pass 

@router.post("/courses/{course_id}/tags")
async def add_tag(db: Annotated[Session, Depends(get_db)], course_id: int, user: TeacherAuthDep, tag: TagBase):
    pass 

@router.delete("/courses/{course_id}/tags/{tag_id}")
async def remove_tag(db: Annotated[Session, Depends(get_db)], course_id: int, tag_id: int, user: TeacherAuthDep):
    pass

@router.post("/approve-enrollment")
def approve_enrollment(db: Annotated[Session, Depends(get_db)], request: EnrollmentApproveRequest, user: TeacherAuthDep):
    pass

@router.patch("/courses/{course_id}/deactivate")
def deactivate_course(course_id, existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
  pass

@router.get("/courses/reports")
def generate_course_reports(existing_teacher: TeacherAuthDep, db: Annotated[Session, Depends(get_db)]):
    pass

  




