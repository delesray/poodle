from sqlalchemy.orm import Session
from database.models import Tag, CourseTag
from schemas.tag import TagBase
from typing import List


async def create_tags(db: Session, tags: List[TagBase], new_course_id: int):
    created_tags = []
    for tag in tags:
        tag_db = Tag(name=tag.name)
        db.add(tag_db)
        db.flush()  # get the tag_id without committing
        course_tag = CourseTag(course_id=new_course_id, tag_id=tag_db.tag_id)
        db.add(course_tag)
        new_tag = TagBase(tag_id=tag_db.tag_id, name=tag_db.name)
        created_tags.append(new_tag)
    db.commit()  
    return created_tags


async def delete_tag(section_id):
    pass

