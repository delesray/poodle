import pytest
from sqlalchemy.orm import Session
from crud import crud_teacher
from db.models import Teacher, Course, Section, Account, Student
from schemas.course import CourseCreate, CourseUpdate
from schemas.teacher import TeacherEdit
from schemas.tag import TagBase
from schemas.section import SectionBase
from tests import dummies


def get_dummy_teacher(teacher_id: int):
    return Teacher(
    teacher_id=teacher_id
)

def get_dummy_course(teacher_id: int, course_id: int):
    return Course(
    course_id=course_id,
    owner_id=teacher_id
)

async def create_dummy_student(db: Session, id: int, email: str, first_name: str, is_premium=0) -> tuple[Account, Student]:
    account_id = id
    account = Account(
        account_id=account_id,
        email=email,
        password='pass',
        role='student',
    )
    student = Student(
        student_id=account_id,
        first_name=first_name,
        last_name='Student',
        is_premium=is_premium
    )
    db.add_all([account, student])
    db.commit()
    return account, student

async def create_dummy_teacher(db: Session, id: int) -> tuple[Account, Teacher]:
    account_id = id
    account = Account(
        account_id=account_id,
        email='t@t.com',
        password='pass',
        role='teacher',
    )
    teacher = Teacher(
        teacher_id=account_id,
        first_name='Dummy',
        last_name='Teacher',
    )
    db.add_all([account, teacher])
    db.commit()
    return account, teacher

async def create_dummy_course(db: Session, teacher: Teacher):
    course = Course(
        course_id=1,
        title="dummy",
        description='dummy',
        objectives='dummy',
        owner_id=teacher.teacher_id,
    )
    db.add(course)
    db.commit()
    return course


async def create_dummy_section(db, section_id, course_id):
    section = Section(
        section_id=section_id,
        title='section',
        content_type='text',
        course_id=course_id
    )
    db.add(section)
    db.commit()

    return section

def create_dummy_sectionbase(section_id=None, course_id=None):
    return SectionBase(
        section_id=section_id,
        title="Test Title",
        content_type="video",
        external_link="http://example.com",
        description="Test Description",
        course_id=course_id   
)

@pytest.mark.asyncio
async def test_edit_account_returns_updated_teacher_account(db):
    _, teacher = await dummies.create_dummy_teacher(db)
    
    updates = TeacherEdit(
        first_name="UpdatedFirst",
        last_name="UpdatedLast",
        phone_number="1234567890",
        linked_in="newLinkedInProfile"
    )

    updated_teacher = await crud_teacher.edit_account(db, teacher, updates)

    assert updated_teacher.first_name == "UpdatedFirst"
    assert updated_teacher.last_name == "UpdatedLast"
    assert updated_teacher.phone_number == "1234567890"
    assert updated_teacher.linked_in == "newLinkedInProfile"
 
    
@pytest.mark.asyncio
async def test_get_my_courses_returns_list_of_courses(db):
    _, teacher = await dummies.create_dummy_teacher(db)
    course = await create_dummy_course(db, teacher)
    
    courses = await crud_teacher.get_my_courses(db, teacher)

    assert len(courses) == 1
    assert courses[0].course_id == course.course_id

   
@pytest.mark.asyncio
async def test_make_course_returns_created_CourseSectionsTags_model(db):
    _, teacher = await dummies.create_dummy_teacher(db)
    new_course = CourseCreate(
        title="New Course",
        description="New Course Description",
        objectives="Objectives",
        is_premium=False,
        tags=[TagBase(name="NewTag")],
        sections=[create_dummy_sectionbase()]
    )

    course_with_tags_and_sections = await crud_teacher.make_course(db, teacher, new_course)

    assert course_with_tags_and_sections.course.title == new_course.title
    assert len(course_with_tags_and_sections.tags) == 1
    assert len(course_with_tags_and_sections.sections) == 1
    
    
@pytest.mark.asyncio
async def test_get_entire_course_returns_CourseSectionsTags_model_with_sorting(db):
    _, teacher = await dummies.create_dummy_teacher(db)
    course = await create_dummy_course(db, teacher)
    tag = await dummies.create_dummy_tag(db)
    await dummies.add_dummy_tag(db, course.course_id, tag.tag_id)
 
    section_1 = await create_dummy_section(db, section_id=1, course_id=course.course_id)
    section_2 = await create_dummy_section(db, section_id=2, course_id=course.course_id)
    
    course_with_details = await crud_teacher.get_entire_course(db, course, teacher, sort='asc', sort_by='section_id')

    assert course_with_details.course.course_id == course.course_id
    assert len(course_with_details.tags) == 1
    assert len(course_with_details.sections) == 2
    assert course_with_details.sections[0].section_id == section_1.section_id
    assert course_with_details.sections[1].section_id == section_2.section_id
 
@pytest.mark.asyncio 
async def test_edit_course_info_returns_updated_course(db):
    _, teacher = await dummies.create_dummy_teacher(db)
    course = await create_dummy_course(db, teacher)

    updates = CourseUpdate(
        title="Updated Title",
        description="Updated Description",
        objectives="Updated Objectives"
    )
    
    updated_course = await crud_teacher.edit_course_info(db, course, teacher, updates)

    assert updated_course.title == "Updated Title"
    assert updated_course.description == "Updated Description"
    assert updated_course.objectives == "Updated Objectives"
    
    
def test_validate_course_access_returns_error_message_when_course_not_exists():
    teacher = get_dummy_teacher(1)

    result, message = crud_teacher.validate_course_access(None, teacher)
    
    assert result is False
    assert message == "Course does not exist"


def test_validate_course_access_returns_error_message_when_teacher_not_own_course():
    teacher_1 = get_dummy_teacher(1)
    teacher_2 = get_dummy_teacher(2)
    course = get_dummy_course(teacher_1.teacher_id, 1)

    result, message = crud_teacher.validate_course_access(course, teacher_2)
    
    assert result is False
    assert message == "You do not have permission to access this course"
    

def test_validate_course_access_returns_OK_message_when_teacher_owns_existing_course():  
    teacher = get_dummy_teacher(1)
    course = get_dummy_course(teacher.teacher_id, 1)
    
    result, message = crud_teacher.validate_course_access(course, teacher)
    
    assert result is True
    assert message == "OK"
 
 
@pytest.mark.asyncio
async def test_get_courses_reports_returns_correct_report_with_filters_by_min_progress(db: Session):
    _, teacher = await create_dummy_teacher(db, id=1)
    course = await create_dummy_course(db, teacher)
    _, student1 = await create_dummy_student(db, id=2,  email="student1@dummymail.com", first_name="DummyName_1")
    _, student2 = await create_dummy_student(db, id=3,  email="student2@dummymail.com", first_name="DummyName_2")
    
    await dummies.subscribe_dummy_student(db, student1.student_id, course.course_id)
    await dummies.subscribe_dummy_student(db, student2.student_id, course.course_id)
    
    section_1 = await create_dummy_section(db, section_id=1, course_id=1)
    section_2 = await create_dummy_section(db, section_id=2, course_id=1)
    section_3 = await create_dummy_section(db, section_id=3, course_id=1)
      
    await dummies.dummy_view_section(db, student1.student_id, section_1.section_id)
    await dummies.dummy_view_section(db, student2.student_id, section_1.section_id)
    await dummies.dummy_view_section(db, student2.student_id, section_2.section_id)
    await dummies.dummy_view_section(db, student2.student_id, section_3.section_id)
     
    reports = await crud_teacher.get_courses_reports(db, teacher, min_progress=25.00, sort='asc')
  
    assert len(reports) == 1
    assert reports[0]['course_id'] == course.course_id
    assert reports[0]['title'] == course.title
    assert len(reports[0]['students']) == 2
    assert reports[0]['students'][0]['student_info'].first_name == student1.first_name
    assert reports[0]['students'][0]['progress'] == '33.33'
    assert reports[0]['students'][1]['student_info'].first_name == student2.first_name
    assert reports[0]['students'][1]['progress'] == '100.00'


@pytest.mark.asyncio
async def test_calculate_student_progresses_returns_dict_with_student_progresses(db: Session):
    _, teacher = await create_dummy_teacher(db, id=1)
    course = await create_dummy_course(db, teacher)
    _, student1 = await create_dummy_student(db, id=2,  email="student1@dummymail.com", first_name="DummyName_1")
    _, student2 = await create_dummy_student(db, id=3,  email="student2@dummymail.com", first_name="DummyName_2")
     
    await dummies.subscribe_dummy_student(db, student1.student_id, course.course_id)
    await dummies.subscribe_dummy_student(db, student2.student_id, course.course_id)
  
    section_1 = await create_dummy_section(db, section_id=1, course_id=1)
    section_2 = await create_dummy_section(db, section_id=2, course_id=1)
    section_3 = await create_dummy_section(db, section_id=3, course_id=1)
    section_4 = await create_dummy_section(db, section_id=4, course_id=1)
      
    await dummies.dummy_view_section(db, student1.student_id, section_1.section_id)
    await dummies.dummy_view_section(db, student1.student_id, section_2.section_id)
    await dummies.dummy_view_section(db, student1.student_id, section_3.section_id)
    await dummies.dummy_view_section(db, student2.student_id, section_4.section_id)
     
    courses_with_students = [course]
    
    student_progress_dict = await crud_teacher.calculate_student_progresses(db, courses_with_students)
    
    assert student_progress_dict[(student1.student_id, course.course_id)] == '75.00'
    assert student_progress_dict[(student2.student_id, course.course_id)] == '25.00'  
 
    
@pytest.mark.asyncio
async def test_calculate_student_progresses_returns_zero_for_courses_with_no_sections(db: Session):
    _, teacher = await create_dummy_teacher(db, id=1)
    course = await create_dummy_course(db, teacher)
    _, student = await create_dummy_student(db, id=2, email="student@dummymail.com", first_name="DummyName_1")
    
    await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)
    
    courses_with_students = [course]
    
    student_progress_dict = await crud_teacher.calculate_student_progresses(db, courses_with_students)
    
    assert student_progress_dict[(student.student_id, course.course_id)] == '0.00'

   
@pytest.mark.asyncio
async def test_generate_reports_returns_reports_filtered_by_min_progress(db: Session):
    _, teacher = await create_dummy_teacher(db, id=1)
    course = await create_dummy_course(db, teacher)
    _, student1 = await create_dummy_student(db, id=2, email="student1@dummymail.com", first_name="DummyName_1")
    _, student2 = await create_dummy_student(db, id=3, email="student2@dummymail.com", first_name="DummyName_2")
     
    await dummies.subscribe_dummy_student(db, student1.student_id, course.course_id)
    await dummies.subscribe_dummy_student(db, student2.student_id, course.course_id)
  
    section_1 = await create_dummy_section(db, section_id=1, course_id=1)
    section_2 = await create_dummy_section(db, section_id=2, course_id=1)
       
    await dummies.dummy_view_section(db, student1.student_id, section_1.section_id)
    await dummies.dummy_view_section(db, student1.student_id, section_2.section_id)
    await dummies.dummy_view_section(db, student2.student_id, section_1.section_id)
     
    student_progress_dict = {
        (student1.student_id, course.course_id): '100.00',
        (student2.student_id, course.course_id): '50.00'
    }
    
    reports = crud_teacher.generate_reports([course], student_progress_dict, min_progress=60.0)
    
    assert len(reports) == 1
    assert reports[0]['course_id'] == course.course_id
    assert len(reports[0]['students']) == 1
    assert reports[0]['students'][0]['student_info'].first_name == student1.first_name
    assert reports[0]['students'][0]['progress'] == '100.00'
    
    reports = crud_teacher.generate_reports([course], student_progress_dict, min_progress=40.0)
    
    assert len(reports) == 1
    assert reports[0]['course_id'] == course.course_id
    assert len(reports[0]['students']) == 2
    assert reports[0]['students'][0]['student_info'].first_name == student1.first_name
    assert reports[0]['students'][0]['progress'] == '100.00'
    assert reports[0]['students'][1]['student_info'].first_name == student2.first_name
    assert reports[0]['students'][1]['progress'] == '50.00'
    
    
@pytest.mark.asyncio
async def test_generate_reports_returns_report_with_empty_list_of_students_when_no_students(db: Session):
    _, teacher = await create_dummy_teacher(db, id=1)
    course = await create_dummy_course(db, teacher)
    
    student_progress_dict = {}
    
    reports = crud_teacher.generate_reports([course], student_progress_dict, min_progress=0.0)
    
    assert len(reports) == 1
    assert reports[0]['course_id'] == course.course_id
    assert len(reports[0]['students']) == 0

    
 
