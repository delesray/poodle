from sqlalchemy.orm import Session

from database.models import Student, StudentCourse, Course, Teacher, StudentRating, Account


def remove_student_from_course(db: Session, student_id: int, course_id) -> None:
    query = (db.query(StudentCourse).filter(
        StudentCourse.student_id == student_id,
        StudentCourse.course_id == course_id
    ).first())

    db.delete(query)
    db.commit()


def hide_course(db: Session, course: Course) -> None:
    course.hidden = True
    db.commit()
    db.refresh(course)


def approve_teacher_registration(db: Session, teacher: Teacher) -> None:
    raise NotImplementedError()


def make_student_premium(db: Session, student: Student) -> None:
    student.premium = True
    db.commit()
    db.refresh(student)


def get_students_ratings_by_course_id(db: Session, course_id: int) -> list[StudentRating]:
    # empty list is ok
    query = (db.query(StudentRating).filter(StudentRating.course_id == course_id))
    return query.all()


def switch_user_activation(db: Session, user: Account):
    user.is_deactivated = not user.is_deactivated
    db.commit()
    db.refresh(user)