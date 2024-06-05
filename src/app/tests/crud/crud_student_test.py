import pytest
from sqlalchemy.orm import Session
from crud.crud_student import is_student_enrolled
from db.models import Account, Student, Course, Teacher, StudentCourse, Status
from crud import crud_student
from fastapi import status, HTTPException


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
async def test_get_student_by_id_returns_student_if_exists(db, test_db):
    account, _ = await create_dummy_student(db)

    res = await crud_student.get_student_by_id(db, account.account_id)
    assert res == account


@pytest.mark.asyncio
async def test_get_student_by_id_raises_404_if_auto_error(db, test_db):
    test_account_id = 3

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
