from fastapi import APIRouter, HTTPException, Body, status
from db.models import Course, Student 
from crud import crud_user, crud_teacher, crud_student
from crud import crud_course, crud_section, crud_tag
from schemas.teacher import TeacherEdit, TeacherCreate, TeacherSchema, TeacherApproveRequest
from schemas.course import CourseCreate, CourseUpdate, CourseSectionsTags, CourseBase, CoursePendingRequests
from schemas.section import SectionBase, SectionUpdate
from schemas.tag import TagBase
from core.oauth import TeacherAuthDep
from schemas.user import UserChangePassword
from api.api_v1.routes import utils
from typing import List, Dict
from typing import Union
from fastapi import UploadFile
from db.database import dbDep

router = APIRouter(prefix='/teachers', tags=['teachers'])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TeacherSchema)
async def register_teacher(db: dbDep, teacher: TeacherCreate):
    """
    Registers a teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherCreate): The information of the teacher to register.

    **Returns**: a TeacherSchema object with the created teacher's details.

    **Raises**:
    - `HTTPException 409`: if a user with the same email has already been registered.
    - `HTTPException 400`: if the account with the same email is deactivated.
    """
    account = await crud_user.email_exists(db, teacher.email)
    if account:
        if account.is_deactivated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account with this email is deactivated"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    return await crud_user.create(db, teacher)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def update_profile_picture(db: dbDep, teacher: TeacherAuthDep, file: UploadFile):
    """
    Lets an authenticated teacher add or edit their profile picture.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authenticated teacher.
    - `file` (UploadFile): The uploaded file containing the image data.

    **Returns**: Successful message, if the picture is uploaded.

    **Raises**: 
    - `HTTPException 401`: if the teacher is not authenticated.
    - `HTTPException 400`, if the file is corruped or the teacher uploaded an unsupported media type.
    """
    if await crud_user.add_picture(db, file, 'teacher', teacher.teacher_id):
        return 'Profile picture successfully uploaded!'
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File is corrupted or media type is not supported"
    )


@router.get('/', response_model=TeacherSchema)
async def view_account(teacher: TeacherAuthDep):
    """
    Shows authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Returns**: a TeacherSchema object with the teacher's account details.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.

    """

    return await crud_teacher.get_info(teacher, teacher.account.email)


@router.put('/', response_model=TeacherSchema)
async def update_account(
        db: dbDep,
        teacher: TeacherAuthDep,
        updates: TeacherEdit = Body(...)
):
    """
    Edits authenticated teacher's profile information.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (TeacherEdit): TeacherEdit object that specifies the desired account updates.

    **Returns**: a TeacherSchema object with the teacher's edited account details.

    **Raises**: 
    - `HTTPException 401`, if the teacher is not authenticated.
    """

    edited_teacher_account = await crud_teacher.edit_account(db, teacher, updates)

    return await crud_teacher.get_info(edited_teacher_account, teacher.account.email)


@router.patch('/', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: dbDep, teacher: TeacherAuthDep,
                          pass_update: UserChangePassword) -> None:
    """
    Changes authenticated teacher's password.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `pass_update` (UserChangePassword): The form for changing teacher's password.

    **Raises**:
    - HTTPException 401, if the teacher is not authenticated.
    - HTTPException 401, if old password does not match.
    - HTTPException 400, if new password is the same as the old one.
    - HTTPException 400, if new password confirmation does not match.
    """
    await utils.change_pass_raise(account=teacher.account, pass_update=pass_update)

    await crud_user.change_password(db=db, pass_update=pass_update, account=teacher.account)


@router.post("/courses", status_code=status.HTTP_201_CREATED, response_model=CourseSectionsTags)
async def create_course(
        db: dbDep,
        teacher: TeacherAuthDep,
        course: CourseCreate
) -> CourseSectionsTags:
    """
    Creates a new course for an authenticated teacher.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `course` (CourseCreate): CourseCreate object that specifies the details of the new course.

    **Returns**: a CourseSectionsTags object with the details, tags, and sections of the created course.

    **Raises**:
    - `HTTPException 409`: If a course with the same title already exists.
    - `HTTPException 401`: If the teacher is not authenticated.

    """
    if await crud_course.course_exists(db, course.title):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course with such title already exists",
        )

    return await crud_teacher.make_course(db, teacher, course)


@router.post('/courses/home-page-picture', status_code=status.HTTP_201_CREATED)
async def update_course_home_page_picture(
        db: dbDep,
        teacher: TeacherAuthDep,
        course_id: int,
        file: UploadFile
):
    """
    Lets an authenticated teacher add or edit the home page picture for a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authenticated teacher.
    - `course_id` (int): The ID of the course for which the home page picture is being updated.
    - `file` (UploadFile): The uploaded file containing the image data.

    **Returns**: A successful message if the picture is uploaded.

    **Raises**: 
    - `HTTPException 401`: if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 400`: If the file is corrupted or the media type is not supported.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    if await crud_user.add_picture(db, file, 'course', course.course_id):
        return 'Home page picture successfully uploaded!'
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File is corrupted or media type is not supported"
    )


@router.get('/courses/pending', response_model=list[CoursePendingRequests])
async def view_pending_requests(db: dbDep, teacher: TeacherAuthDep):
    """
    Returns authenticated teacher's pending requests for courses.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.

    **Returns**: A list of CoursePendingRequests response models with the course title and student email for each enrollment request.
    """
    return await crud_teacher.view_pending_requests(db, teacher)


@router.get("/courses", response_model=list[CourseBase])
async def get_courses(db: dbDep, teacher: TeacherAuthDep):
    """
    Returns teacher's courses.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.

    **Raises**:
    - `HTTPException 401`, If the teacher is not authenticated.

    **Returns**: A list of CourseBase response models containing information about courses owned by the teacher.
    """

    return await crud_teacher.get_my_courses(db, teacher)


@router.get("/courses/{course_id}", response_model=CourseSectionsTags)
async def view_course_by_id(
        db: dbDep,
        course_id: int,
        teacher: TeacherAuthDep,
        sort: str | None = None,
        sort_by: str | None = None
):
    """
    Retrieves a course by its ID along with associated tags and sections.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course to retrieve.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `sort` (str, optional): Sort order, either 'asc' or 'desc'.
    - `sort_by` (str, optional): Field to sort by, either 'section_id' or 'title'.
    
    **Returns**: A `CourseSectionsTags` object containing the course details, tags, and sections.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 400`: If the sort or sort_by parameters are invalid.
    - `HTTPException 403`: If the authenticated teacher does not have permission to access the course.
    """
    if sort and sort.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter"
        )

    if sort_by and sort_by.lower() not in ['section_id', 'title']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by parameter"
        )

    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    return await crud_teacher.get_entire_course(db, course, teacher, sort, sort_by)


@router.put("/courses/requests", status_code=status.HTTP_201_CREATED)
async def approve_enrollment(db: dbDep,
                             teacher: TeacherAuthDep,
                             student: str,
                             course_id: int,
                             response: TeacherApproveRequest):
    """
    Enables a course owner to approve/deny requests for enrollment by students.
    An email notification is sent to the student after the request is approved or denied.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `student` (string): The student's email.
    - `course_id` (integer): The ID of the course.
    - `response` (string): The response of the request. Could be either 'Approve' or 'Deny'.
    
    **Returns**: A message, if the response is successfully submitted.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 404`, if the student or the course is not found.
    - `HTTPException 403`, if the teacher is not the owner of the course.
    """

    course: Course = await crud_course.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such course')

    if not await crud_teacher.is_teacher_owner(course_id, teacher):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Course owner required')

    student: Student = await crud_student.get_by_email(db, student)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No student with such email')

    return await crud_teacher.student_enroll_response(db, student, teacher, course, response.value)


@router.put("/courses/{course_id}", response_model=CourseBase)
async def update_course_info(
        db: dbDep,
        course_id: int,
        teacher: TeacherAuthDep,
        updates: CourseUpdate = Body(...)
):
    """
    Updates the information of a specific course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course to update.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (CourseUpdate): The updated course information.

    **Returns**: A `CourseBase` object containing the updated course details.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the authenticated teacher does not have permission to update the course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    return await crud_teacher.edit_course_info(db, course, teacher, updates)


@router.put("/courses/{course_id}/sections/{section_id}", response_model=SectionBase)
async def update_section(
        db: dbDep,
        course_id: int,
        section_id: int,
        teacher: TeacherAuthDep,
        updates: SectionUpdate = Body(...)
):
    """
    Updates the information of a specific section within a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course containing the section to update.
    - `section_id` (int): The ID of the section to update.
    - `user` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `updates` (SectionUpdate): The updated section information.

    **Returns**: A `SectionBase` object containing the updated section details.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the authenticated teacher does not have permission to update the section.
    - `HTTPException 404`: If the section with the given ID does not exist or is not part of the specified course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    section = await crud_section.get_section_by_id(db, section_id)
    valid_section, msg = crud_section.validate_section(section, course_id)
    if not valid_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )

    return await crud_section.update_section_info(db, section, updates)


@router.post("/courses/{course_id}/sections", status_code=status.HTTP_201_CREATED, response_model=List[SectionBase])
async def add_sections(
        db: dbDep,
        course_id: int,
        teacher: TeacherAuthDep,
        sections: List[SectionBase]
):
    """
    Create sections for a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course for which sections are being created.
    - `teacher` (TeacherAuthDep): The authentication dependency for users with role Teacher.
    - `sections` (List[SectionBase]): A list of SectionBase objects containing section details.

    **Returns:** A list of newly created sections.

    **Raises:**
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have permission to add sections to the course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    created_sections = await crud_section.create_sections(db, sections, course_id)
    return created_sections


@router.delete("/courses/{course_id}/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_section(
        db: dbDep,
        course_id: int,
        section_id: int,
        teacher: TeacherAuthDep
):
    """
    Removes a section from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course.
    - `section_id` (int): The ID of the section to remove.
    - `teacher` (TeacherAuthDep): The authenticated teacher.

    **Returns**: HTTP status 204 (No Content) if successful.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 404`: If the section is not found or does not belong to the specified course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    section = await crud_section.get_section_by_id(db, section_id)
    valid_section, msg = crud_section.validate_section(section, course_id)
    if not valid_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )

    await crud_section.delete_section(db, section)
    return


@router.post("/courses/{course_id}/tags", status_code=status.HTTP_201_CREATED,
             response_model=Dict[str, List[Union[TagBase, int]]])
async def add_tags(
        db: dbDep,
        course_id: int,
        teacher: TeacherAuthDep,
        tags: List[TagBase]
):
    """
    Add tags to a course.

    **Parameters:**
    - `db` (Session)`: The SQLAlchemy db session.
    - `course_id` (int)`: The ID of the course for which tags are being created.
    - `teacher` (TeacherAuthDep)`: The authentication dependency for users with the Teacher role.
    - `tags` (List[TagBase])`: A list of TagBase objects containing tag details.

    **Returns:** A dictionary with:
    - `created` (List[TagBase])`: A list of newly created TagBase objects.
    - `duplicated_tags_ids` (List[int])`: A list of tag IDs that already existed for the course.

    **Raises:**
    - `HTTPException 401`: If the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have permission to add tags to the course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    created_tags = await crud_tag.create_tags(db, tags, course_id)
    return created_tags


@router.delete("/courses/{course_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(
        db: dbDep,
        course_id: int,
        tag_id: int,
        teacher: TeacherAuthDep
):
    """
    Removes a tag from a course.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course.
    - `tag_id` (int): The ID of the tag to remove.
    - `teacher` (TeacherAuthDep): The authenticated teacher.

    **Returns**: HTTP status 204 (No Content) if successful.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 404`: If the tag is not associated with the course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    course_tag = await crud_tag.course_has_tag(db, course_id, tag_id)
    if not course_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID:{tag_id} not associated with course ID:{course_id}"
        )

    await crud_tag.delete_tag_from_course(db, course_tag)

    tag_associations = await crud_tag.check_tag_associations(db, tag_id)
    if tag_associations == 0:
        await crud_tag.delete_tag(db, tag_id)

    return


@router.patch("/courses/{course_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_course(db: dbDep, course_id: int, teacher: TeacherAuthDep):
    """
    Deactivates a course if the teacher owns it and no students are enrolled.

    **Parameters:**
    - `db` (Session): The SQLAlchemy db session.
    - `course_id` (int): The ID of the course to deactivate.
    - `teacher` (TeacherAuthDep): The authenticated teacher.

    **Returns**: HTTP status 204 (No Content) if successful.

    **Raises**:
    - `HTTPException 401`, if the teacher is not authenticated.
    - `HTTPException 403`: If the teacher does not have access to the course.
    - `HTTPException 400`: If there are students enrolled in the course.
    """
    course = await crud_course.get_course_common_info(db, course_id)
    user_has_access, msg = crud_teacher.validate_course_access(course, teacher)
    if not user_has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg
        )

    if course.students_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate a course with enrolled students"
        )
    await crud_course.hide_course(db, course)
    return


@router.get("/reports")
async def generate_courses_reports(
        db: dbDep,
        teacher: TeacherAuthDep,
        min_progress: str = "0.0",
        sort: str | None = None
):
    """
    Generate reports for courses owned by the authenticated teacher, with options for sorting and filtering by student progress.

    **Parameters:**
    - `db` (AsyncSession): The SQLAlchemy db session.
    - `teacher` (TeacherAuthDep): The authenticated teacher.
    - `min_progress` (str): The minimum progress percentage to filter students. Defaults to "0.0".
    - `sort` (str | None): Optional sorting order for courses, either 'asc' or 'desc'. Defaults to None.

    **Returns**: A list of courses with student progress reports.

    **Raises**: 
    - `HTTPException 401`: if the teacher is not authenticated.
    - `HTTPException 400`: If the `min_progress` parameter is invalid.
    - `HTTPException 400`: If the `sort` parameter is invalid.
    """
    try:
        min_progress = round(float(min_progress), 2)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid min_progress parameter"
        )

    if sort and sort.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter"
        )

    return await crud_teacher.get_courses_reports(db, teacher, min_progress, sort)
