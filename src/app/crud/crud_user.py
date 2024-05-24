from sqlalchemy.orm import Session
from schemas.user import UserChangePassword
from schemas.teacher import TeacherCreate, TeacherResponseModel
from schemas.student import StudentCreate, StudentResponseModel
from database.models import Account, Teacher, Student
from core.hashing import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Union, Type
from core import hashing


async def create_user(db: Session, user: Union[StudentCreate, TeacherCreate]):
    new_user = Account(
        email=user.email,
        password=hash_pass(user.password),
        role=user.get_type()
    )

    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_user)
        return new_user


class TeacherFactory():
    @staticmethod
    async def create_db_user(db: Session, user_schema: Union[StudentCreate, TeacherCreate]):
        new_user = await create_user(db, user_schema)

        new_teacher = Teacher(
            teacher_id=new_user.account_id,
            first_name=user_schema.first_name,
            last_name=user_schema.last_name,
            phone_number=user_schema.phone_number,
            linked_in=user_schema.linked_in,
            profile_picture=user_schema.profile_picture
        )

        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        #await send_verification_email([schema.email], new_user)
        return TeacherResponseModel(
            teacher_id=new_user.account_id,
            email=new_user.email,
            first_name=new_teacher.first_name,
            last_name=new_teacher.last_name,
            phone_number=new_teacher.phone_number,
            linked_in=new_teacher.linked_in,
            profile_picture=new_teacher.profile_picture   
        )


class StudentFactory():
    @staticmethod
    async def create_db_user(db: Session, user_schema: Union[StudentCreate, TeacherCreate]):
        new_user = await create_user(db, user_schema)

        new_student = Student(
            student_id=new_user.account_id,
            first_name=user_schema.first_name,
            last_name=user_schema.last_name,
            profile_picture=user_schema.profile_picture
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return StudentResponseModel(
            first_name=new_student.first_name, 
            last_name=new_student.last_name, 
            profile_picture=new_student.profile_picture)


def create_user_factory(user_type: str):
    factories = {
        "teacher": TeacherFactory,
        "student": StudentFactory
    }
    return factories.get(user_type)


async def create(db: Session, user_schema: Union[StudentCreate, TeacherCreate]) -> Union[Teacher, Student]:
    user_type = user_schema.get_type()
    factory = create_user_factory(user_type)
    return await factory.create_db_user(db, user_schema)


async def exists(db: Session, email: str):
    query = db.query(Account).filter(Account.email == email,
                                     Account.is_deactivated == False).first()

    if query:
        return query


async def try_login(db: Session, username: str, password: str) -> Type[Account]:
    user = await exists(db, username)

    if user and hashing.verify_password(password, user.password):
        return user


async def change_password(db: Session, pass_update: UserChangePassword, account: Account):
    hashed_pass = hashing.hash_pass(pass_update.new_password)
    account.password = hashed_pass

    db.commit()


async def check_deactivated(user: Union[Student, Teacher]):
    if user.is_deactivated:
        raise HTTPException(
            status_code=404,
            detail="User is deactivated",
        )
