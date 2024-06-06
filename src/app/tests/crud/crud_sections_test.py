from unittest.mock import Mock

import pytest
from tests import dummies
from crud import crud_section


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
