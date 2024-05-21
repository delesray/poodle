from sqlalchemy.orm import Session
from database.models import Account, Student
from schemas.student import StudentResponseModel


async def get_student(db: Session, email: str):
    student = (
        db.query(Student)
        .join(Student.account)
        .filter(Account.email == email)
        .first()
    )

    if student:
        return StudentResponseModel(
            first_name=student.first_name,
            last_name=student.last_name,
            profile_picture=student.profile_picture,
            is_premium=student.is_premium,
            is_deactivated=student.is_deactivated
        )
