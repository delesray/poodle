import pytest
from sqlalchemy.orm import Session
from crud.crud_student import is_student_enrolled
from db.models import Account, Student, Course, Teacher, StudentCourse, Status
from crud import crud_student
from fastapi import status, HTTPException

from schemas.course import CourseInfo
from schemas.student import StudentResponseModel, StudentEdit


async def get_non_existent_account_id():
    non_existent_account_id = 3
    return non_existent_account_id


async def get_non_existent_email():
    non_existent_email = 'dummyMail@mail.com'
    return non_existent_email


async def create_dummy_student(db: Session) -> tuple[Account, Student]:
    account_id = 1
    account = Account(
        account_id=account_id,
        email='s@s.com',
        password='pass',
        role='student',
    )
    student = Student(
        student_id=account_id,
        first_name='Dummy',
        last_name='Student'
    )
    db.add_all([account, student])
    db.commit()
    return account, student


async def create_dummy_teacher(db: Session):
    account_id = 2
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


async def create_dummy_course(db: Session):
    _, teacher = await create_dummy_teacher(db)
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


async def subscribe_dummy_student(db: Session, student_id, course_id):
    enrollment = StudentCourse(
        student_id=student_id,
        course_id=course_id,
        status=Status.active.value,
    )
    db.add(enrollment)
    db.commit()
    return enrollment


@pytest.mark.asyncio
async def test_unsubscribe_student(db, test_db):
    _, student = await create_dummy_student(db)
    course = await create_dummy_course(db)
    enrollment = await subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value
    assert enrollment.student_id == student.student_id
    assert enrollment.course_id == course.course_id

    # act
    await crud_student.unsubscribe_from_course(db, student.student_id, course.course_id)

    res = await is_student_enrolled(student, course.course_id)
    assert res is False


@pytest.mark.asyncio
async def test_get_student_by_id_returns_student_if_exists(db, test_db):
    account, _ = await create_dummy_student(db)

    res = await crud_student.get_student_by_id(db, account.account_id)
    assert res == account


@pytest.mark.asyncio
async def test_get_student_by_id_raises_404_if_auto_error(db, test_db):
    test_account_id = await get_non_existent_account_id()

    with pytest.raises(HTTPException) as exc_info:
        await crud_student.get_student_by_id(db, test_account_id, auto_error=True)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert str(exc_info.value.detail) == 'No such user'


@pytest.mark.asyncio
async def test_get_student_by_email_returns_student_if_exists(db, test_db):
    account, student = await create_dummy_student(db)

    res = await crud_student.get_by_email(db, account.email)
    assert res == student


@pytest.mark.asyncio
async def test_get_student_returns_student_response_model_if_exists(db, test_db):
    account, student = await create_dummy_student(db)

    res = await crud_student.get_student(db, account.email)

    assert isinstance(res, StudentResponseModel)
    assert res.first_name == student.first_name
    assert res.last_name == student.last_name


@pytest.mark.asyncio
async def test_get_student_returns_none_if_no_student(db, test_db):
    test_account_email = await get_non_existent_email()
    res = await crud_student.get_student(db, test_account_email)

    assert res is None


@pytest.mark.asyncio
async def test_get_edit_student_account_returns_edited_student_response_model(db, test_db):
    account, student = await create_dummy_student(db)

    res = await crud_student.get_by_email(db, account.email)
    assert res == student

    updates = StudentEdit(first_name='new_name', last_name='new_last_name')

    edited = await crud_student.edit_account(db, account.email, updates)

    assert isinstance(edited, StudentResponseModel)
    assert edited.first_name == student.first_name
    assert edited.last_name == student.last_name


@pytest.mark.asyncio
async def test_get_courses_returns_empty_list_when_no_courses(db, test_db):
    _, student = await create_dummy_student(db)

    res = await crud_student.get_my_courses(student)

    assert res == []


@pytest.mark.asyncio
async def test_get_courses_returns_courses_list(db, test_db):
    _, student = await create_dummy_student(db)
    course = await create_dummy_course(db)
    enrollment1 = await subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment1.status == Status.active.value

    res = await crud_student.get_my_courses(student)

    assert res == [CourseInfo(title='dummy', description='dummy', is_premium=False, tags=[])]
