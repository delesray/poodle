import pytest
from crud.crud_student import is_student_enrolled
from db.models import Status
from crud import crud_student
from fastapi import status, HTTPException
from schemas.course import CourseInfo
from schemas.student import StudentResponseModel, StudentEdit
from tests import dummies


@pytest.mark.asyncio
async def test_unsubscribe_student(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value
    assert enrollment.student_id == student.student_id
    assert enrollment.course_id == course.course_id

    # act
    await crud_student.unsubscribe_from_course(db, student.student_id, course.course_id)

    res = await is_student_enrolled(student, course.course_id)
    assert res is False


@pytest.mark.asyncio
async def test_get_student_by_id_returns_student_if_exists(db):
    account, _ = await dummies.create_dummy_student(db)

    res = await crud_student.get_student_by_id(db, account.account_id)
    assert res == account


@pytest.mark.asyncio
async def test_get_student_by_id_raises_404_if_auto_error(db):
    test_account_id = await dummies.get_non_existent_account_id()

    with pytest.raises(HTTPException) as exc_info:
        await crud_student.get_student_by_id(db, test_account_id, auto_error=True)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == 'No such user'


@pytest.mark.asyncio
async def test_get_student_by_email_returns_student_if_exists(db):
    account, student = await dummies.create_dummy_student(db)

    res = await crud_student.get_by_email(db, account.email)
    assert res == student


@pytest.mark.asyncio
async def test_get_student_returns_student_response_model_if_exists(db):
    account, student = await dummies.create_dummy_student(db)

    res = await crud_student.get_student(db, account.email)

    assert isinstance(res, StudentResponseModel)
    assert res.first_name == student.first_name
    assert res.last_name == student.last_name


@pytest.mark.asyncio
async def test_get_student_returns_none_if_no_student(db):
    test_account_email = await dummies.get_non_existent_email()
    res = await crud_student.get_student(db, test_account_email)

    assert res is None


@pytest.mark.asyncio
async def test_get_edit_student_account_returns_edited_student_response_model(db):
    account, student = await dummies.create_dummy_student(db)

    res = await crud_student.get_by_email(db, account.email)
    assert res == student

    updates = StudentEdit(first_name='new_name', last_name='new_last_name')

    edited = await crud_student.edit_account(db, account.email, updates)

    assert isinstance(edited, StudentResponseModel)
    assert edited.first_name == student.first_name
    assert edited.last_name == student.last_name


@pytest.mark.asyncio
async def test_get_courses_returns_empty_list_when_no_courses(db):
    _, student = await dummies.create_dummy_student(db)

    res = await crud_student.get_my_courses(student)

    assert res == []


@pytest.mark.asyncio
async def test_get_courses_returns_courses_list(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment1 = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment1.status == Status.active.value

    res = await crud_student.get_my_courses(student)

    assert res == [CourseInfo(title='dummy', description='dummy', is_premium=False, tags=[])]


@pytest.mark.asyncio
async def test_is_student_enrolled_returns_false_when_not_enrolled(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)

    res = await crud_student.is_student_enrolled(student, course.course_id)

    assert res is False


@pytest.mark.asyncio
async def test_is_student_enrolled_returns_true_when_enrolled(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.is_student_enrolled(student, course.course_id)

    assert res is True


@pytest.mark.asyncio
async def test_get_premium_courses_count_returns_correct_count(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    course.is_premium = True
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.get_premium_courses_count(student)

    assert res == 1


@pytest.mark.asyncio
async def test_get_premium_courses_count_returns_correct_zero_when_no_premium_courses(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.get_premium_courses_count(student)

    assert res == 0


@pytest.mark.asyncio
async def test_get_student_rating_when_has_rated(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    await dummies.dummy_student_rating(db, student.student_id, course.course_id)
    res = await crud_student.get_student_rating(db, student.student_id, course.course_id)

    assert res == await dummies.get_default_tst_rating()


@pytest.mark.asyncio
async def test_get_student_rating_when_has_rated(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.get_student_rating(db, student.student_id, course.course_id)

    assert res is None