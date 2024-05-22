from sqlalchemy.orm import Session
from database.models import Teacher
from schemas.teacher import TeacherResponseModel

async def update(existing_teacher, teacher):
    pass

async def create_new_course(new_course, existing_teacher):
    pass

async def edit_course(course_id, course_update):
    pass

async def get_teacher_by_id(db: Session, id: int):
    teacher = (db.query(Teacher).filter(Teacher.teacher_id == id, Teacher.is_deactivated == False).first())
    return teacher

async def get_info(teacher, teacher_email):
    return TeacherResponseModel(
            teacher_id=teacher.teacher_id,
            email=teacher_email,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            phone_number=teacher.phone_number,
            linkedin=teacher.linked_in, 
            profile_picture=teacher.profile_picture
        )
