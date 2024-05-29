from sqlalchemy.orm import Session

from database.models import Student, StudentCourse, Course


def remove_student_from_course(db: Session, student_id: int, course_id) -> None:
    query = (db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id
    ).first())

    db.delete(query)
    db.commit()


def hide_course(db: Session, course_id: Course) -> None:
    course_id.hidden = True
    db.commit()
