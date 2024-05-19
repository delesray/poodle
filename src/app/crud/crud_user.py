from sqlalchemy.orm import Session
from src.app.schemas.user import User
from src.app.schemas.teacher import Teacher
from src.app.schemas.student import Student
from src.app.database.models import Account, Teacher, Admin, Student
from src.app.core.hashing import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


async def create_user(db: Session, teacher: User):
    # await send_email([schema.email], new_user)
    new_teacher = Account(
        email=teacher.email,
        hashed_password=hash_pass(teacher.password)
    )

    try:
        db.add(new_teacher)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_teacher)
        return new_teacher


# def create_user_factory(user_type: str):
#     factories = {
#         "teacher": Teacher,
#         "student": Student
#     }
#     return factories.get(user_type,

# TODO discuss - other join or role column in accounts
async def find_by_email(db: Session, email: str):
    query = db.query(Account) \
        .outerjoin(Student) \
        .outerjoin(Teacher) \
        .outerjoin(Admin) \
        .filter(Account.email == email)

    return query.first()
