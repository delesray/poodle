from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from crud.crud_user import create, exists
from crud import crud_teacher
from crud.crud_course import course_exists, get_course_common_info
from crud.crud_section import create_sections, get_section_by_id, update_section_info, delete_section
from crud.crud_tag import create_tags, delete_tag_from_course, course_has_tag, check_tag_associations, delete_tag
from schemas.teacher import TeacherEdit, TeacherCreate, TeacherSchema
from schemas.course import CourseCreate, CourseUpdate, CourseSectionsTags, CourseBase
from schemas.student import EnrollmentApproveRequest
from schemas.section import SectionBase, SectionUpdate
from schemas.tag import TagBase
from core.oauth import TeacherAuthDep
from typing import List

router = APIRouter(prefix='/teachers', tags=['teachers'])


@router.post("/register", status_code=201, response_model=TeacherSchema)
async def register_teacher(db: Annotated[Session, Depends(get_db)], teacher: TeacherCreate):
    """
    Registers a teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherCreate): The information of the teacher to register.

    **Returns**: a TeacherSchema object with the created teacher's details.

    **Raises**: HTTPException 409, if a user with the same email has already been registered.

    """
    if await exists(db, teacher.email):
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )
    #new_teacher = await create(db, user)
    return await create(db, teacher)

@router.get('/', response_model=TeacherSchema)
async def view_account(db: Annotated[Session, Depends(get_db)], teacher: TeacherAuthDep):
    """
    Shows authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Returns**: a TeacherSchema object with the teacher's account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.

    """

    return await crud_teacher.get_info(teacher, teacher.account.email)


@router.put('/', response_model=TeacherSchema)
async def update_account(
        db: Annotated[Session, Depends(get_db)],
        teacher: TeacherAuthDep,
        updates: TeacherEdit = Body(...)
):
    """
    Edits authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (TeacherEdit): TeacherEdit object that specifies the desired account updates.

    **Returns**: a TeacherSchema object with the teacher's edited account details.

    **Raises**: HTTPException 401, if the teacher is not authenticated.
    """

    edited_teacher_account = await crud_teacher.edit_account(db, teacher, updates)

    return await crud_teacher.get_info(edited_teacher_account, teacher.account.email)


@router.post("/courses", status_code=201, response_model=CourseSectionsTags)
async def create_course(
        db: Annotated[Session, Depends(get_db)],
        teacher: TeacherAuthDep,
        course: CourseCreate
) -> CourseSectionsTags:
    """
    Creates a new course for an authenticated teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
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

    return await crud_teacher.make_course(db, teacher, course)


@router.get("/courses", response_model=list[CourseBase])
async def get_courses(db: Annotated[Session, Depends(get_db)], teacher: TeacherAuthDep):
    """
    Returns teacher's courses.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Raises**:
    - HTTPException 401, If the teacher is not authenticated.

    **Returns**: A list of CourseBase response models containing information about courses owned by the teacher.
    """

    return await crud_teacher.get_my_courses(db, teacher)



@router.get("/courses/{course_id}", response_model=CourseSectionsTags)
async def view_course_by_id(
        db: Annotated[Session, Depends(get_db)],
        course_id: int,
        teacher: TeacherAuthDep,
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
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 400`: If the sort or sort_by parameters are invalid.
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
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )

    return await crud_teacher.get_entire_course(db, course, teacher, sort, sort_by)


@router.put("/courses/{course_id}", response_model=CourseBase)
async def update_course_info(
        db: Annotated[Session, Depends(get_db)],
        course_id: int,
        teacher: TeacherAuthDep,
        updates: CourseUpdate = Body(...)
):
    """
    Updates the information of a specific course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course to update.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (CourseUpdate): The updated course information.

    **Returns**: A `CourseBase` object containing the updated course details.

    **Raises**:
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the authenticated teacher does not have permission to update the course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
        
    return await crud_teacher.edit_course_info(db, course, teacher, updates)


@router.put("/courses/{course_id}/sections/{section_id}", response_model=SectionBase)
async def update_section(
    db: Annotated[Session, Depends(get_db)], 
    course_id: int,
    section_id: int,
    teacher: TeacherAuthDep, 
    updates: SectionUpdate = Body(...)
):
    """
    Updates the information of a specific section within a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course containing the section to update.
    - `section_id` (int): The ID of the section to update.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (SectionUpdate): The updated section information.

    **Returns**: A `SectionBase` object containing the updated section details.

    **Raises**:
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the authenticated teacher does not have permission to update the section.
    - `HTTPException 404`: If the section with the given ID does not exist or is not part of the specified course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        ) 
        
    section = await get_section_by_id(db, section_id)
    valid_section, msg = await crud_teacher.validate_section(section, course_id)
    if not valid_section:
        raise HTTPException(
            status_code=404,
            detail=msg
        )
        
    return await update_section_info(db, section, updates)

        

@router.post("/courses/{course_id}/sections", status_code=201, response_model=List[SectionBase])
async def add_sections(
    db: Annotated[Session, Depends(get_db)], 
    course_id: int, 
    teacher: TeacherAuthDep, 
    sections: List[SectionBase]
): 
    """
    Create sections for a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course for which sections are being created.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `sections` (List[SectionBase]): A list of SectionBase objects containing section details.

    **Returns:** A list of newly created sections.

    **Raises:**
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have permission to add sections to the course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
        
    created_sections = await create_sections(db, sections, course_id)
    return created_sections
         
         
@router.delete("/courses/{course_id}/sections/{section_id}", status_code=204)
async def remove_section(
    db: Annotated[Session, Depends(get_db)],
    course_id: int,
    section_id: int,
    teacher: TeacherAuthDep
): 
    """
    Removes a section from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course.
    - `section_id` (int): The ID of the section to remove.
    - `teacher` (TeacherAuthDep): The authenticated teacher.

    **Returns**: HTTP status 204 (No Content) if successful.

    **Raises**:
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 404`: If the section is not found or does not belong to the specified course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
    
    section = await get_section_by_id(db, section_id)
    valid_section, msg = await crud_teacher.validate_section(section, course_id)
    if not valid_section:
        raise HTTPException(
            status_code=404,
            detail=msg
        )
    
    await delete_section(db, section)
    return


@router.post("/courses/{course_id}/tags", status_code=201, response_model=List[TagBase])
async def add_tags(
    db: Annotated[Session, Depends(get_db)],
    course_id: int, 
    teacher: TeacherAuthDep,
    tags: List[TagBase]
):
    """
    Create tags for a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course for which tags are being created.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `tags` (List[TagBase]): A list of TagBase objects containing tag details.

    **Returns:** A list of newly created tags.

    **Raises:**
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have permission to add tags to the course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
        
    created_tags = await create_tags(db, tags, course_id)
    return created_tags

@router.delete("/courses/{course_id}/tags/{tag_id}", status_code=204)
async def remove_tag(
    db: Annotated[Session, Depends(get_db)], 
    course_id: int, 
    tag_id: int, 
    teacher: TeacherAuthDep
):
    """
    Removes a tag from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy database session.
    - `course_id` (int): The ID of the course.
    - `tag_id` (int): The ID of the tag to remove.
    - `teacher` (TeacherAuthDep): The authenticated teacher.

    **Returns**: HTTP status 204 (No Content) if successful.

    **Raises**:
    - 'HTTPException 401', if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 404`: If the tag is not associated with the course.
    """
    course = await get_course_common_info(db, course_id)
    user_has_access, msg = await crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
    
    course_tag = await course_has_tag(db, course_id, tag_id)    
    if not course_tag:
        raise HTTPException(
            status_code=404,
            detail=f"Tag with ID:{tag_id} not associated with course ID:{course_id}"
        )
     
    await delete_tag_from_course(db, course_tag)
    
    tag_associations = await check_tag_associations(db, tag_id)
    if tag_associations == 0:
        await delete_tag(db, tag_id)
        
    return


@router.post("/approve-enrollment")
def approve_enrollment(db: Annotated[Session, Depends(get_db)], request: EnrollmentApproveRequest,
                       teacher: TeacherAuthDep):
    pass


@router.patch("/courses/{course_id}/deactivate")
def deactivate_course(db: Annotated[Session, Depends(get_db)], course_id, teacher: TeacherAuthDep):
    pass


@router.get("/courses/reports")
def generate_course_reports(db: Annotated[Session, Depends(get_db)], teacher: TeacherAuthDep):
    pass
