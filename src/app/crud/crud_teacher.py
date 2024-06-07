from sqlalchemy.orm import Session, joinedload
from db.models import Course, Student, StudentCourse, Teacher, Tag, CourseTag, Section, Status
from schemas.course import CourseCreate, CourseBase, CoursePendingRequests, CourseSectionsTags, CourseUpdate
from crud.crud_section import create_sections, transfer_object
from crud.crud_tag import create_tags
from crud.crud_student import get_student_progress
from schemas.teacher import TeacherSchema, TeacherEdit
from schemas.tag import TagBase
from email_notification import build_teacher_enroll_request, send_email
from schemas.student import StudentResponseModel
from sqlalchemy.future import select
from typing import List, Dict


async def edit_account(db: Session, teacher: Teacher, updates: TeacherEdit):
    teacher.first_name = updates.first_name
    teacher.last_name = updates.last_name
    teacher.phone_number = updates.phone_number
    teacher.linked_in = updates.linked_in

    db.commit()
    db.refresh(teacher)

    return teacher


async def get_info(teacher: Teacher, teacher_email: str):
    return TeacherSchema(
        teacher_id=teacher.teacher_id,
        email=teacher_email,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        phone_number=teacher.phone_number,
        linked_in=teacher.linked_in,
    )


async def get_my_courses(db: Session, teacher: Teacher) -> list[CourseBase]:
    courses = db.query(Course).filter(Course.owner_id == teacher.teacher_id).all()

    teacher_courses = [get_coursebase_model(teacher, course) for course in courses]
    return teacher_courses


async def make_course(db: Session, teacher: Teacher, new_course: CourseCreate):
    course_info = Course(
        title=new_course.title,
        description=new_course.description,
        objectives=new_course.objectives,
        owner_id=teacher.teacher_id,
        is_premium=new_course.is_premium
    )

    db.add(course_info)
    db.commit()
    db.refresh(course_info)

    course_info_response = get_coursebase_model(teacher, course_info)
    course_tags, course_sections = [], []
    if new_course.tags:
        created_tags = await create_tags(db, new_course.tags, course_info.course_id)
        course_tags = created_tags.get("created")
    if new_course.sections:
        course_sections = await create_sections(db, new_course.sections, course_info.course_id)

    return CourseSectionsTags(
        course=course_info_response,
        tags=course_tags,
        sections=course_sections
    )


async def get_entire_course(db: Session, course: Course, teacher: Teacher, sort: str | None, sort_by: str | None):
    course_info = get_coursebase_model(teacher, course)

    course_tags = []
    tags = db.query(Tag).join(CourseTag).filter(CourseTag.course_id == course.course_id).all()
    for tag in tags:
        tag_base = TagBase(tag_id=tag.tag_id, name=tag.name)
        course_tags.append(tag_base)

    course_sections = []
    sections_query = db.query(Section).filter(Section.course_id == course.course_id)
    if sort_by:
        sections_query = sections_query.order_by(
            getattr(Section, sort_by).desc() if sort and sort == 'desc' else getattr(Section, sort_by).asc()
        )

    sections = sections_query.all()
    for section in sections:
        section_base = transfer_object(section)
        course_sections.append(section_base)

    return CourseSectionsTags(
        course=course_info,
        tags=course_tags,
        sections=course_sections
    )


async def edit_course_info(db: Session, course: Course, teacher: Teacher, updates: CourseUpdate):
    course.title = updates.title
    course.description = updates.description
    course.objectives = updates.objectives
    db.commit()
    db.refresh(course)

    return get_coursebase_model(teacher, course)


def validate_course_access(course: Course, teacher: Teacher) -> tuple[bool, str]:
    if not course:
        return False, f"Course does not exist"

    if course.owner_id != teacher.teacher_id:
        return False, f"You do not have permission to access this course"

    return True, "OK"


def get_coursebase_model(teacher: Teacher, course: Course):
    return CourseBase(
        course_id=course.course_id,
        title=course.title,
        description=course.description,
        objectives=course.objectives,
        owner_id=course.owner_id,
        owner_names=f"{teacher.first_name} {teacher.last_name}",
        is_premium=course.is_premium,
        rating=course.rating,
        people_rated=course.people_rated
    )


async def student_enroll_response(db: Session, student: Student, teacher: Teacher, course: Course, response: str):
    sc_record = db.query(StudentCourse).filter(StudentCourse.student_id == student.student_id,
                                               StudentCourse.course_id == course.course_id).first()

    sc_record.status = Status.active.value if response == 'approve' else Status.declined.value
    db.commit()

    response = True if sc_record.status == Status.active.value else False
    return await send_notification(receiver_mail=student.account.email,
                                   course_title=course.title,
                                   response=response)


async def is_teacher_owner(course_id: int, teacher: Teacher):
    return course_id in set([course.course_id for course in teacher.courses])


async def send_notification(receiver_mail: str, course_title: str, response: bool):
    request = await build_teacher_enroll_request(receiver_mail, course_title, response)
    await send_email(data=request)

    return 'Request response submitted'


async def view_pending_requests(db: Session, teacher: Teacher):
    res = (db.query(Course, Student)
           .join(StudentCourse, StudentCourse.course_id == Course.course_id)
           .join(Student, Student.student_id == StudentCourse.student_id)
           .join(Teacher, Course.owner_id == Teacher.teacher_id)
           .filter(StudentCourse.status == Status.pending.value)
           .all()
           )

    return [CoursePendingRequests.from_query(course.title, student.account.email) for course, student in res]


async def calculate_student_progresses(db: Session, courses_with_students: List[Course]) -> Dict[int, str]:
    student_progress_dict = {}

    for course in courses_with_students:
        for student in course.students_enrolled:
            if student.student_id not in student_progress_dict:
                student_progress = await get_student_progress(db, student.student_id, course.course_id)
                student_progress_dict[student.student_id] = student_progress

    return student_progress_dict


async def get_courses_reports(db: Session, teacher: Teacher, min_progress: float, sort: str = None):
    courses_query = (
        select(Course)
        .options(joinedload(Course.students_enrolled))
        .where(Course.owner_id == teacher.teacher_id)
    )
    
    if sort == 'asc':
        courses_query = courses_query.order_by(Course.course_id.asc())
    elif sort == 'desc':
        courses_query = courses_query.order_by(Course.course_id.desc())
    
    result = db.execute(courses_query)
    courses_with_students = result.scalars().unique().all()

    student_progress_dict = await calculate_student_progresses(db, courses_with_students)
    courses_reports = generate_reports(courses_with_students, student_progress_dict, min_progress)

    return courses_reports


def generate_reports(courses_with_students: List[Course], student_progress_dict: Dict[int, str], min_progress: float):
    reports = []
    for course in courses_with_students:
        students = [
            {
                "student_info": StudentResponseModel.from_query(student.first_name, student.last_name, student.is_premium),
                "progress": student_progress_dict[student.student_id]
            }
            for student in course.students_enrolled
            if float(student_progress_dict[student.student_id]) >= min_progress  
        ]
        course_report = {
            "course_id": course.course_id,
            "title": course.title,
            "students": students
        }
        reports.append(course_report)
    
    return reports
