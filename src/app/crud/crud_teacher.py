from sqlalchemy.orm import Session
from database.models import Teacher, Course
from schemas.teacher import TeacherResponseModel, TeacherEdit


async def edit_account(db: Session, teacher: Teacher, updates: TeacherEdit):  
    teacher.first_name = updates.first_name
    teacher.last_name = updates.last_name
    teacher.phone_number = updates.phone_number
    teacher.linked_in = updates.linked_in
    teacher.profile_picture = updates.profile_picture

    db.commit()
    #db.refresh(teacher)

    return f"Your account has been successfully updated"


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

async def get_course_by_id(db: Session, id: int):
    course = (db.query(Course).filter(Course.id == id).first())
    return course