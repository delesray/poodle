from sqlalchemy.orm import Session

from db.models import Account, Student, Teacher, Course, StudentCourse, Status, Admin, Section


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


dummy_admin_id = 3
dummy_user = Account(
    account_id=dummy_admin_id,
    email='dummy@admin.com',
    password='dummypass',
    role='admin',
    is_deactivated=False,
)
dummy_admin = Admin(
    admin_id=dummy_admin_id,
    account=dummy_user,
)


async def create_dummy_admin(db: Session):
    db.add_all([dummy_user, dummy_admin])
    db.commit()
    return dummy_user, dummy_admin


NON_EXISTING_ID = 999


async def create_dummy_section(db):
    course = await create_dummy_course(db)
    section = Section(
        section_id=1,
        title='section',
        content_type='txt',
        course_id=course.course_id,
    )
    return section, course
