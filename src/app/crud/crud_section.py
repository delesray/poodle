from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database.models import Section, StudentsSections
from schemas.section import SectionBase
from typing import List


async def get_section_by_id(db, section_id) -> Section:
    section = db.query(Section).where(Section.id == section_id).first()

    if section:
        return section


async def create_sections(db: Session, sections: List[SectionBase], new_course_id: int):
    created_sections = []
    for section in sections:
        section_db = Section(
            title=section.title,
            content=section.content,
            description=section.description,
            external_link=section.external_link,
            course_id=new_course_id
        )
        db.add(section_db)
        db.flush()  # get the section_id without committing

        new_section = SectionBase.from_query(
            section_db.section_id, section_db.title, section_db.content,
            section_db.description, section_db.external_link, section_db.course_id
        )

        created_sections.append(new_section)

    db.commit()

    return created_sections


async def add_student(db: Session, section_id, student_id):
    new = StudentsSections(section_id=section_id, student_id=student_id)
    try:  # todo Nora refresh
        db.add(new)
        db.commit()
    except IntegrityError:
        pass
    return SectionBase.from_query(
        new.section_id,
        new.title,
        new.content,
        new.description,
        new.external_link,
        new.course_id,
    )


async def update_section(section_id, section_update):
    pass


async def delete_section(section_id):
    pass
