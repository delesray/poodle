import pytest
from crud import crud_tag
from tests import dummies


@pytest.mark.asyncio
async def test_create_tags_returns_dict_with_created_tags_when_no_duplicates(db):
    dummy_tags = [await dummies.create_dummy_tag_base(tag_id=1, name='dummyTag1'),
                  await dummies.create_dummy_tag_base(tag_id=2, name='dummyTag2')]

    course = await dummies.create_dummy_course(db)

    res = await crud_tag.create_tags(db, dummy_tags, course.course_id)

    assert res == {
        "created": dummy_tags,
        "duplicated_tags_ids": []
    }


@pytest.mark.asyncio
async def test_create_tags_returns_dict_with_created_tags_when_has_duplicates(db):
    dummy_tags = [await dummies.create_dummy_tag_base(tag_id=1, name='dummyTag'),
                  await dummies.create_dummy_tag_base(tag_id=2, name='dummyTag2')]

    course = await dummies.create_dummy_course(db)
    tag = await dummies.create_dummy_tag(db)
    await dummies.add_dummy_tag(db, course.course_id, tag.tag_id)

    res = await crud_tag.create_tags(db, dummy_tags, course.course_id)

    assert res == {
        "created": [dummy_tags[1]],
        "duplicated_tags_ids": [1]
    }


@pytest.mark.asyncio
async def test_course_has_tags_returns_course_tags_if_tags_exist(db):
    course = await dummies.create_dummy_course(db)
    tag = await dummies.create_dummy_tag(db)
    course_tag = await dummies.add_dummy_tag(db, course.course_id, tag.tag_id)

    res = await crud_tag.course_has_tag(db, course.course_id, tag.tag_id)

    assert res == course_tag


@pytest.mark.asyncio
async def test_course_has_tags_returns_none_if_not_tags(db):
    course = await dummies.create_dummy_course(db)
    tag = await dummies.create_dummy_tag(db)
    res = await crud_tag.course_has_tag(db, course.course_id, tag.tag_id)

    assert res is None


@pytest.mark.asyncio
async def test_check_tag_associations_returns_tag_count_if_tags_exist(db):
    course = await dummies.create_dummy_course(db)
    tag = await dummies.create_dummy_tag(db)
    await dummies.add_dummy_tag(db, course.course_id, tag.tag_id)

    res = await crud_tag.check_tag_associations(db, tag.tag_id)

    assert res == 1


@pytest.mark.asyncio
async def test_check_tag_associations_returns_zero_if_not_tags(db):
    tag = await dummies.create_dummy_tag(db)

    res = await crud_tag.check_tag_associations(db, tag.tag_id)

    assert res == 0
