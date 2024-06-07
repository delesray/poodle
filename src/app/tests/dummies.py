from sqlalchemy.orm import Session

from db.models import Account, Student, Teacher, Course, StudentCourse, Status, Admin, Section, StudentRating, \
    StudentSection, Tag, CourseTag
from schemas.tag import TagBase


async def get_non_existent_account_id():
    non_existent_account_id = 3
    return non_existent_account_id


async def get_non_existent_email():
    non_existent_email = 'dummyMail@mail.com'
    return non_existent_email


async def get_default_tst_rating():
    default_tst_rating = 5
    return default_tst_rating


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


async def subscribe_dummy_student(db: Session, student_id, course_id, status=Status.active.value):
    enrollment = StudentCourse(
        student_id=student_id,
        course_id=course_id,
        status=status,
    )
    db.add(enrollment)
    db.commit()
    return enrollment


async def dummy_student_rating(db: Session, student_id, course_id):
    rating = await get_default_tst_rating()
    new_rating = StudentRating(
        student_id=student_id,
        course_id=course_id,
        rating=rating)
    db.add(new_rating)
    db.commit()


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


async def dummy_view_section(db, student_id, section_id):
    visited_section = StudentSection(student_id=student_id,
                                     section_id=section_id)

    db.add(visited_section)
    db.commit()


async def create_dummy_tag(db):
    tag = Tag(tag_id=1, name='dummyTag')
    db.add(tag)
    db.commit()

    return tag


async def add_dummy_tag(db, course_id, tag_id):
    add_tag = CourseTag(course_id=course_id, tag_id=tag_id)
    db.add(add_tag)
    db.commit()

    return add_tag


async def create_dummy_tag_base(tag_id, name):
    return TagBase(tag_id=tag_id, name=name)
