import pytest
from crud.crud_student import is_student_enrolled
from db.models import Status, Section
from crud import crud_student
from fastapi import status, HTTPException
from schemas.course import CourseInfo, CourseRateResponse, StudentCourseSchema
from schemas.student import StudentResponseModel, StudentEdit
from tests import dummies


async def create_dummy_section(db, course_id):
    section = Section(
        section_id=1,
        title='section',
        content_type='text',
        course_id=course_id
    )
    db.add(section)
    db.commit()

    return section


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
async def test_get_student_rating_when_not_has_rated(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.get_student_rating(db, student.student_id, course.course_id)

    assert res is None


@pytest.mark.asyncio
async def test_get_student_progress_when_not_has_progress(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    res = await crud_student.get_student_progress(db, student.student_id, course.course_id)

    assert res == '0.00'


@pytest.mark.asyncio
async def test_get_student_progress_when_has_progress(db):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    section = await create_dummy_section(db, course.course_id)
    await dummies.dummy_view_section(db, student.student_id, section.section_id)

    res = await crud_student.get_student_progress(db, student.student_id, course.course_id)

    assert res == '100.00'


@pytest.mark.asyncio
async def test_update_add_student_rating_when_no_existing_rating(db, mocker):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    rating = await crud_student.get_student_rating(db, student.student_id, course.course_id)

    assert rating is None

    mocker.patch('crud.crud_student.crud_course.update_rating', return_value=None)
    rating = await dummies.get_default_tst_rating()
    res = await crud_student.update_add_student_rating(db, student, course.course_id, rating)

    assert isinstance(res, CourseRateResponse)
    assert res.course == course.title
    assert res.rating == rating


@pytest.mark.asyncio
async def test_update_add_student_rating_when_existing_rating(db, mocker):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    enrollment = await dummies.subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value

    rating = await crud_student.get_student_rating(db, student.student_id, course.course_id)

    assert rating is None

    mocker.patch('crud.crud_student.crud_course.update_rating', return_value=None)
    rating = await dummies.get_default_tst_rating()
    res = await crud_student.update_add_student_rating(db, student, course.course_id, rating)

    assert isinstance(res, CourseRateResponse)
    assert res.course == course.title
    assert res.rating == rating

    new_rating = 7
    new_res = await crud_student.update_add_student_rating(db, student, course.course_id, new_rating)

    assert isinstance(new_res, CourseRateResponse)
    assert new_res.course == course.title
    assert new_res.rating == new_rating


@pytest.mark.asyncio
async def test_get_course_information_when_course(db, mocker):
    _, student = await dummies.create_dummy_student(db)
    course = await dummies.create_dummy_course(db)
    tst_progress = 100.0

    mocker.patch('crud.crud_student.crud_course.get_course_common_info',
                 return_value=course)
    mocker.patch('crud.crud_student.get_student_rating',
                               return_value=await dummies.get_default_tst_rating())
    mocker.patch('crud.crud_student.get_student_progress',
                                 return_value=tst_progress)

    res = await crud_student.get_course_information(db, course.course_id, student)

    assert isinstance(res, StudentCourseSchema)
    assert res.course_id == course.course_id
    assert res.title == course.title
    assert res.owner_id == course.owner_id
    assert res.owner_name == 'Dummy Teacher'
    assert res.your_rating == await dummies.get_default_tst_rating()
    assert res.your_progress == tst_progress


@pytest.mark.asyncio
async def test_get_course_information_when_no_course(db, mocker):
    _, student = await dummies.create_dummy_student(db)
    tst_course_id = 5

    mocker.patch('crud.crud_student.crud_course.get_course_common_info',
                 return_value=None)

    res = await crud_student.get_course_information(db, tst_course_id, student)

    assert res is None


@pytest.mark.asyncio
async def test_send_notification_returns_correct_msg():
    pass
