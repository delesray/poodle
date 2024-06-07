import pytest
from sqlalchemy.orm import Session
from crud import crud_teacher
from db.models import Teacher, Course, Status, Section
from fastapi import status, HTTPException
from schemas.course import CourseCreate, CourseInfo
from schemas.teacher import TeacherEdit
from schemas.tag import TagBase
from schemas.section import SectionBase
from tests import dummies


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
 
 