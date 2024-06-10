from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from crud import crud_course
from db.models import Account, Course, Status, Student, StudentCourse as DBStudentCourse, StudentRating, StudentSection, \
    Section
from schemas.student import StudentEdit, StudentResponseModel
from schemas.course import CourseInfo, CourseRateResponse, StudentCourseSchema
from email_notification import send_email, build_student_enroll_request


async def get_student_by_id(db: Session, user_id: int, auto_error=False) -> Account | None:
    query = (db.query(Account)
             .filter(Account.account_id == user_id, Account.is_deactivated == False)
             .first())

    if query:
        return query
    if auto_error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such user')


async def get_by_email(db: Session, email: str) -> Student | None:
    student = (db.query(Student).join(Student.account).filter(
        Account.email == email, Account.is_deactivated == False).first())

    if student:
        return student


async def get_student(db: Session, email: str) -> StudentResponseModel | None:
    student = await get_by_email(db, email)

    if student:
        return StudentResponseModel.from_query(student.first_name, student.last_name, student.is_premium)


async def edit_account(db: Session, email: str, updates: StudentEdit) -> StudentResponseModel:
    student = await get_by_email(db, email)

    student.first_name, student.last_name = updates.first_name, \
        updates.last_name

    db.commit()
    db.refresh(student)

    return StudentResponseModel.from_query(student.first_name, student.last_name, student.is_premium)


async def get_my_courses(student: Student) -> list[CourseInfo]:
    my_courses = student.courses_enrolled

    my_courses_pydantic: list[CourseInfo] = []
    for c in my_courses:
        tags = [str(t) for t in c.tags]
        my_courses_pydantic.append(CourseInfo.from_query(
            *(c.title, c.description, c.is_premium, tags)))

    return my_courses_pydantic


async def add_pending_student_request(db: Session, student: Student, course_id: int) -> None:
    pending_enrollment = DBStudentCourse(
        student_id=student.student_id,
        course_id=course_id
    )

    try:
        db.add(pending_enrollment)
        db.commit()

    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)

    else:
        db.refresh(pending_enrollment)


async def unsubscribe_from_course(db: Session, student_id: int, course_id: int) -> None:
    db.query(DBStudentCourse).filter(DBStudentCourse.student_id ==
                                     student_id, DBStudentCourse.course_id == course_id).delete()
    db.commit()


async def is_student_enrolled(student: Student, course_id: int) -> bool:
    return course_id in set([course.course_id for course in student.courses_enrolled])


async def get_premium_courses_count(student: Student) -> int:
    return len([course for course in student.courses_enrolled if course.is_premium])


async def get_student_rating(db: Session, student_id: int, course_id: int) -> StudentRating | None:
    query = db.query(StudentRating).filter(StudentRating.student_id ==
                                           student_id, StudentRating.course_id == course_id).first()

    if query:
        return query.rating


async def get_student_progress(db: Session, student_id: int, course_id: int) -> str:
    """Gets the count of sections and sections_viewed to calculate the progress in percentage"""
    total_sections = db.query(Section).where(Section.course_id == course_id).count()

    viewed_sections = (
        db.query(StudentSection)
        .join(Section, StudentSection.section_id == Section.section_id)
        .filter(StudentSection.student_id == student_id, Section.course_id == course_id)
        .count()
    )

    progress = 0.0
    if total_sections > 0:  # avoiding zero division
        progress = (viewed_sections / total_sections) * 100

    return f'{progress:.2f}'


async def update_add_student_rating(db: Session, student: Student, course_id: int,
                                    rating: int) -> CourseRateResponse | str:
    existing_rating = db.query(StudentRating).filter(
        StudentRating.student_id == student.student_id,
        StudentRating.course_id == course_id
    ).first()

    try:
        if existing_rating:
            await crud_course.update_rating(db, course_id, rating, existing_rating.rating)
            existing_rating.rating = rating
        else:  # create new one if student still not rated
            new_rating = StudentRating(
                student_id=student.student_id, course_id=course_id, rating=rating)
            db.add(new_rating)

            await crud_course.update_rating(db, course_id, rating)
        db.commit()

        course = next(
            (course for course in student.courses_enrolled if course.course_id == course_id), None)
    except Exception as e:
        db.rollback()

        return str(e)

    return CourseRateResponse(course=course.title, rating=f'{rating:.2f}')


async def get_course_information(db: Session, course_id: int, student: Student) -> StudentCourseSchema:
    course: Course = await crud_course.get_course_common_info(db=db, course_id=course_id)

    if course:
        student_rating = await get_student_rating(db=db, student_id=student.student_id, course_id=course_id)
        student_progress = await get_student_progress(db=db, student_id=student.student_id, course_id=course_id)

        return StudentCourseSchema(
            course_id=course.course_id,
            title=course.title,
            description=course.description,
            objectives=course.objectives,
            owner_id=course.owner_id,
            owner_name=course.owner.first_name + ' ' + course.owner.last_name,
            is_premium=course.is_premium,
            overall_rating=course.rating,
            your_rating=student_rating if student_rating else 0,
            your_progress=student_progress
        )


async def subscribe(db: Session, course: Course, student: Student) -> str:
    teacher_email = course.owner.account.email
    student_email = student.account.email
    course_title, course_id = course.title, course.course_id
    await add_pending_student_request(db, student, course_id)

    try:
        request = await build_student_enroll_request(receiver_mail=teacher_email,
                                                     student_email=student_email,
                                                     course_title=course_title,
                                                     course_id=course_id)
        await send_email(data=request)

        return 'Pending approval from course owner'

    except Exception:
        db.rollback()
        return 'Subscription failed. Please try again later'


async def view_pending_requests(db: Session, student: Student) -> list[CourseInfo]:
    res = db.query(Course).join(DBStudentCourse).filter(DBStudentCourse.student_id == student.student_id,
                                                        DBStudentCourse.course_id == Course.course_id,
                                                        DBStudentCourse.status == Status.pending.value).all()

    if res:
        return [CourseInfo.from_query(course.title,
                                      course.description,
                                      course.is_premium,
                                      [tag.name for tag in course.tags])
                for course in res]
