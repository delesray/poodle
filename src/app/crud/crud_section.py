from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import crud_student
from database.models import Section, StudentSection
from schemas.section import SectionBase
from typing import List


async def get_section_by_id(db, section_id) -> Section:
    section = db.query(Section).where(Section.section_id == section_id).first()

    if section:
        return section


async def create_sections(db: Session, sections: List[SectionBase], course_id: int):
    created_sections = []
    for section in sections:
        section_db = Section(
            title=section.title,
            content_type=section.content_type,
            content=section.content,
            description=section.description,
            external_link=section.external_link,
            course_id=course_id
        )
        db.add(section_db)
        db.flush()  # get the section_id without committing

        new_section = SectionBase.from_query(
            section_db.section_id, section_db.title, section_db.content_type, section_db.content,
            section_db.description, section_db.external_link, section_db.course_id
        )

        created_sections.append(new_section)

    db.commit()

    return created_sections


async def student_viewed_section(db: Session, section_id, student_id):
    data = (db.query(StudentSection)
            .where(StudentSection.section_id == section_id, StudentSection.student_id == student_id)
            .first()
            )
    return data is not None


async def add_student(db: Session, section: Section, student_id) -> None:
    """
    Student views a section (inserts a record in students_sections table)
    IntegrityError means there is already such record and continues
    """
    if await student_viewed_section(db, section.section_id, student_id):
        return
    new = StudentSection(section_id=section.section_id, student_id=student_id)
    db.add(new)
    db.commit()


async def update_section_info(db, section, updates):
    section.title = updates.title
    section.content_type = updates.content_type
    section.content = updates.content
    section.description = updates.description
    section.external_link = updates.external_link
    
    db.commit()
    db.refresh(section)

    return SectionBase.from_query(
            section.section_id, section.title, section.content_type, section.content,
            section.description, section.external_link, section.course_id
        )

async def delete_section(db, section: Section):
    db.delete(section)
    db.commit()


async def get_sections_count_for_course(db: Session, course_id: int) -> int:
    count = db.query(Section).where(Section.course_id == course_id).count()
    return count


def transfer_object(section: Section) -> SectionBase:
    dto = SectionBase(
        section_id=section.section_id,
        title=section.title,
        content_type=section.content_type,
        description=section.description,
        external_link=section.external_link,
        course_id=section.course_id
    )
    return dto

async def validate_section(section: Section, course_id: int) -> tuple[bool, str]:
    if not section:
        return False, f"Section not found"
    
    if section.course_id != course_id:
        return False, f"Section ID:{section.section_id} is not a part of course ID{course_id}"
    
    return True, "OK"
        