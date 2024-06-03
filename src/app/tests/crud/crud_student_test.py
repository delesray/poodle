import pytest
from sqlalchemy.orm import Session

from crud.crud_student import is_student_enrolled
from crud.crud_user import StudentFactory, TeacherFactory
from db.models import Account, Student, Course, Teacher, StudentCourse, Status
from crud import crud_student
from schemas.student import StudentCreate
from schemas.teacher import TeacherCreate


async def create_dummy_student(db: Session, is_premium=0) -> tuple[Account, Student]:
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
        last_name='Student',
        # is_premium=is_premium,
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
    account, student = await create_dummy_student(db)
    course = await create_dummy_course(db)
    enrollment = await subscribe_dummy_student(db, student.student_id, course.course_id)

    assert enrollment.status == Status.active.value
    assert enrollment.student_id == student.student_id
    assert enrollment.course_id == course.course_id

    # act
    await crud_student.unsubscribe_from_course(db, student.student_id, course.course_id)

    res = await is_student_enrolled(student, course.course_id)
    assert res == False
