from sqlalchemy.orm import Session
from db.models import Tag, CourseTag
from schemas.tag import TagBase
from typing import List, Dict
from typing import Union

async def create_tags(db: Session, tags: List[TagBase], course_id: int)-> Dict[str, List[Union[TagBase, int]]]:
    created_tags = []
    duplicated = []
    for tag in tags:
        tag_db = db.query(Tag).filter_by(name=tag.name).first()
        if not tag_db:
            tag_db = Tag(name=tag.name)
            db.add(tag_db)
            db.flush()  # get the tag_id without committing

        course_tag = db.query(CourseTag).filter_by(course_id=course_id, tag_id=tag_db.tag_id).first()
        if course_tag:
            duplicated.append(tag_db.tag_id)
        else:    
            course_tag = CourseTag(course_id=course_id, tag_id=tag_db.tag_id)
            db.add(course_tag)
            new_tag = TagBase(tag_id=tag_db.tag_id, name=tag_db.name)
            created_tags.append(new_tag)
    
    db.commit()
 
    result = {
        "created": created_tags,
        "duplicated_tags_ids": duplicated    
    }
    return result


async def course_has_tag(db: Session, course_id: int, tag_id: int):
    course_tag = db.query(CourseTag).filter_by(course_id=course_id, tag_id=tag_id).first()
    
    return course_tag 
    
    
async def delete_tag_from_course(db: Session, course_tag: CourseTag):
    db.delete(course_tag)
    db.commit()

async def check_tag_associations(db: Session, tag_id: int):   
    tag_associations = db.query(CourseTag).filter_by(tag_id=tag_id).count()
    return tag_associations

async def delete_tag(db: Session, tag_id: int):
        tag = db.query(Tag).filter_by(tag_id=tag_id).first()
        if tag:
            db.delete(tag)
            db.commit()   
