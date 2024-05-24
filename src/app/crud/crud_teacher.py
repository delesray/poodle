from sqlalchemy.orm import Session
from database.models import Course, Teacher, Tag, CourseTag, Section
from schemas.course import CourseCreate, CourseBase, CourseSectionsTags
from crud.crud_section import create_sections
from crud.crud_tag import create_tags
from schemas.teacher import TeacherResponseModel, TeacherEdit
from schemas.tag import TagBase
from schemas.section import SectionBase


async def edit_account(db: Session, teacher: Teacher, updates: TeacherEdit):  
    teacher.first_name = updates.first_name
    teacher.last_name = updates.last_name
    teacher.phone_number = updates.phone_number
    teacher.linked_in = updates.linked_in
    teacher.profile_picture = updates.profile_picture

    db.commit()
    db.refresh(teacher)

    return teacher


async def get_teacher_by_id(db: Session, id: int):
    teacher = (db.query(Teacher).filter(Teacher.teacher_id == id).first())
    return teacher


async def get_info(teacher, teacher_email):
    return TeacherResponseModel(
            teacher_id=teacher.teacher_id,
            email=teacher_email,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            phone_number=teacher.phone_number,
            linked_in=teacher.linked_in, 
            profile_picture=teacher.profile_picture
        )


async def get_my_courses(db: Session, teacher: Teacher) -> list[CourseBase]:
    courses = db.query(Course).filter(Course.owner_id == teacher.teacher_id).all()

    teacher_courses = [
        CourseBase(
            course_id=course.id,
            title=course.title,
            description=course.description,
            objectives=course.objectives,
            owner_id=course.owner_id,
            owner_names=f"{teacher.first_name} {teacher.last_name}",
            is_premium=course.is_premium,
            is_hidden=course.is_hidden,
            home_page_picture=course.home_page_picture,
            rating=course.rating
        ) for course in courses
    ]
    
    return teacher_courses


async def make_course(db: Session, teacher: Teacher, new_course: CourseCreate):
    course_info = Course(
        title=new_course.title,
        description=new_course.description,
        objectives=new_course.objectives,
        owner_id=teacher.teacher_id,
        is_premium=new_course.is_premium,
        is_hidden=False,
        home_page_picture=new_course.home_page_picture,
        rating=0
    )

    db.add(course_info)
    db.commit()
    db.refresh(course_info)
    course_info_response = CourseBase(
        course_id=course_info.id,
        title=course_info.title,
        description=course_info.description,
        objectives=course_info.objectives,
        owner_id=course_info.owner_id,
        owner_names=teacher.first_name + ' ' + teacher.last_name,
        is_premium=course_info.is_premium,
        is_hidden=course_info.is_hidden,
        home_page_picture=course_info.home_page_picture,
        rating=course_info.rating
    )
    course_tags = await create_tags(db, new_course.tags, course_info.id)
    course_sections = await create_sections(db, new_course.sections, course_info.id)
    
    return CourseSectionsTags(
        course=course_info_response,
        tags=course_tags,
        sections=course_sections
    )


async def get_entire_course(db: Session, course: Course, teacher: Teacher):
    course_info = CourseBase(
        course_id=course.id,
        title=course.title,
        description=course.description,
        objectives=course.objectives,
        owner_id=course.owner_id,
        owner_names=f"{teacher.first_name} {teacher.last_name}",
        is_premium=course.is_premium,
        is_hidden=course.is_hidden,
        home_page_picture=course.home_page_picture,
        rating=course.rating
    )
    
    course_tags = []
    tags = db.query(Tag).join(CourseTag).filter(CourseTag.course_id == course.id).all()
    for tag in tags:
        tag_base = TagBase(tag_id=tag.tag_id, name=tag.name)
        course_tags.append(tag_base)
    
    course_sections = []
    sections = db.query(Section).filter(Section.course_id == course.id).all()
    for section in sections:
        section_base = SectionBase.from_query(
            section_id=section.section_id,
            title=section.title,
            content=section.content,
            description=section.description,
            external_link=section.external_link,
            course_id=section.course_id
        )
        course_sections.append(section_base) 
    
    return CourseSectionsTags(
        course=course_info,
        tags=course_tags,
        sections=course_sections
    )
    
async def edit_course_info(course_id, course_update):
    pass