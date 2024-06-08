from unittest.mock import Mock

import pytest
from tests import dummies
from crud import crud_section
from schemas.section import SectionBase, SectionUpdate


def create_dummy_sectionbase(title, section_id=None, course_id=None):
    return SectionBase(
        section_id=section_id,
        title=title,
        content_type="video",
        external_link="http://example.com",
        description="Test Description",
        course_id=course_id   
)


@pytest.mark.asyncio
async def test_add_student_if_student_viewed_section(db, mocker):
    mocker.patch('crud.crud_section.student_viewed_section', return_value=True)

    section, course = await dummies.create_dummy_section(db)

    res = await crud_section.add_student(db=db, section=section, student_id=2)

    assert res is None


def test_validate_section_1(db):
    res, _ = crud_section.validate_section(section=None, course_id=1)

    assert res is False


@pytest.mark.asyncio
async def test_validate_section_happy(db):
    section, course = await dummies.create_dummy_section(db)
    res, _ = crud_section.validate_section(section=section, course_id=course.course_id)

    assert res is True
    
    
@pytest.mark.asyncio
async def test_create_sections_returns_list_of_created_sections(db):
    course = await dummies.create_dummy_course(db)

    sections_data = [
        create_dummy_sectionbase(title="Test Title 1", section_id=1, course_id=1),
        create_dummy_sectionbase(title="Test Title 2", section_id=2, course_id=1)
    ]

    created_sections = await crud_section.create_sections(db, sections_data, course.course_id)

    assert len(created_sections) == 2
    assert created_sections[0].section_id == 1
    assert created_sections[0].title == "Test Title 1"
    assert created_sections[0].course_id == course.course_id
    assert created_sections[1].section_id == 2
    assert created_sections[1].title == "Test Title 2"
    assert created_sections[1].course_id == course.course_id


@pytest.mark.asyncio
async def test_update_section_info(db):
    section, course = await dummies.create_dummy_section(db)

    updates = SectionUpdate(
        title="Updated Section Title",
        content_type="quiz",
        external_link="http://updatedlink.com",
        description="Updated Description"
    )

    updated_section = await crud_section.update_section_info(db, section, updates)

    assert updated_section.title == "Updated Section Title"
    assert updated_section.content_type == "quiz"
    assert updated_section.external_link == "http://updatedlink.com"
    assert updated_section.description == "Updated Description"
    assert updated_section.course_id == course.course_id
    
    