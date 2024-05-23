from sqlalchemy.orm import Session
from database.models import Course, Teacher
from schemas.course import CourseCreate, CourseUpdate, CourseBase

async def get_by_id(course_id):
    #Teachers must be able to view their own courses
    pass

async def get_courses(existing_teacher):
    #Teachers must be able to view their own courses
    pass

async def make_course(db: Session, teacher: Teacher, course: CourseCreate):
    new_course = Course(
        title=course.title,
        description=course.description,
        objectives=course.objectives,
        owner_id=teacher.teacher_id,
        is_premium=course.is_premium,
        is_hidden=False,
        home_page_picture=course.home_page_picture,
        rating=0    
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return CourseBase(
        course_id=new_course.id,
        title=new_course.title,
        description=new_course.description,
        objectives=new_course.objectives,
        owner_id=new_course.owner_id,
        is_premium=new_course.is_premium,
        is_hidden=new_course.is_hidden,
        home_page_picture=new_course.home_page_picture,
        rating=new_course.rating
    )
 

async def edit_course(course_id, course_update):
    pass

async def get_all_courses(
    #Admins could be able to view a list with all public and premium courses, the number of students in them and their rating
        page: int,
        size: int,
        search: str = None,
        owner_id: int = None,
        student_id: int = None
        ):
    pass

async def course_exists(db: Session, title: str):
    query = db.query(Course).filter(Course.title == title).first()

    return query is not None