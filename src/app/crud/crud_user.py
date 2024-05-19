from sqlalchemy.orm import Session
from schemas.user import User
from schemas.teacher import Teacher
# from src.app.schemas.student import Student
from database.models import Account, Teacher, Admin, Student
from core.hashing import hash_pass
from sqlalchemy.exc import IntegrityError, DataError
from fastapi import HTTPException, status


async def create_user(db: Session, user: User):
    # await send_email([schema.email], new_user)
    new_user = Account(
        email=user.email,
        password=hash_pass(user.password),
        role=user.role
    )

    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)
    except DataError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='Invalid role type. Please choose between <teacher> and <student>')
    else:
        db.refresh(new_user)
        return new_user.account_id


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
