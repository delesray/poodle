from sqlalchemy import update
from sqlalchemy.orm import Session
from database.models import Account, Student
from schemas.student import StudentEdit, StudentResponseModel


async def get_by_email(db: Session, email: str):
    student = (db.query(Student).join(Student.account).filter(
        Account.email == email, Student.is_deactivated == False).first())

    if student:
        return student


async def get_student(db: Session, email: str):
    student = await get_by_email(db, email)

    if student:
        return StudentResponseModel(
            first_name=student.first_name,
            last_name=student.last_name,
            profile_picture=student.profile_picture,
            is_premium=student.is_premium,
            is_deactivated=student.is_deactivated
        )


async def edit_account(db: Session, email: str, updates: StudentEdit):
    student = await get_by_email(db, email)

    student.first_name, student.last_name, student.profile_picture = updates.first_name, updates.last_name, updates.profile_picture

    db.commit()

    return StudentResponseModel(
        first_name=updates.first_name,
        last_name=updates.last_name,
        profile_picture=updates.profile_picture,
        is_premium=student.is_premium,
        is_deactivated=student.is_deactivated
    )
