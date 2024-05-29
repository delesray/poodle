from sqlalchemy.orm import Session

from database.models import Student, StudentCourse


def remove_student_from_course(db: Session, student_id: int, course_id) -> None:
    query = (db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id
    ).first())

    if query is not None:
        db.delete(query)
        db.commit()
        return True
    return None
