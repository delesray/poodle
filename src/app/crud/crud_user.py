from io import BytesIO
from sqlalchemy import update
from sqlalchemy.orm import Session
from schemas.user import UserChangePassword
from schemas.teacher import TeacherCreate, TeacherSchema
from schemas.student import StudentCreate, StudentResponseModel
from db.models import Account, Teacher, Student, Course
from core.hashing import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, UploadFile
from typing import Union, Type
from core import hashing
from PIL import Image, UnidentifiedImageError

DEFAULT_PICTURE_WIDTH = 400
DEFAULT_PICTURE_HEIGHT = 400


class Role:
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'
    UNION = Union[Student, Teacher, Account]


async def get_user_by_id_deactivated_also(db: Session, user_id: int) -> Account | None:
    query = (db.query(Account)
             .filter(Account.account_id == user_id)
             .first())
    return query


async def get_specific_user_or_raise_404(db: Session, user_id: int, role=None) -> Role.UNION | None:
    query = (db.query(Account)
             .filter(Account.account_id == user_id, Account.is_deactivated == False)
             .first())

    if query:  # Just means there is such account
        # Following checks specifically
        if role == Role.STUDENT and query.student:
            return query.student
        if role == Role.TEACHER and query.teacher:
            return query.teacher
        if role == Role.ADMIN and query.admin:
            return query.admin

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No such {role} user')


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
        )

        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        # await send_verification_email([schema.email], new_user)
        return TeacherSchema(
            teacher_id=new_user.account_id,
            email=new_user.email,
            first_name=new_teacher.first_name,
            last_name=new_teacher.last_name,
            phone_number=new_teacher.phone_number,
            linked_in=new_teacher.linked_in
        )


class StudentFactory:
    @staticmethod
    async def create_db_user(db: Session, user_schema: Union[StudentCreate, TeacherCreate]):
        new_user = await create_user(db, user_schema)

        new_student = Student(
            student_id=new_user.account_id,
            first_name=user_schema.first_name,
            last_name=user_schema.last_name
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return StudentResponseModel.from_query(first_name=new_student.first_name, last_name=new_student.last_name)


def create_user_factory(user_type: str):
    factories = {
        "teacher": TeacherFactory,
        "student": StudentFactory
    }
    return factories.get(user_type)


async def create(db: Session, user_schema: Union[StudentCreate, TeacherCreate]) -> Union[
    TeacherSchema, StudentResponseModel]:
    user_type = user_schema.get_type()
    factory = create_user_factory(user_type)
    return await factory.create_db_user(db, user_schema)


async def exists(db: Session, email: str) -> Account:
    query = db.query(Account).filter(
        Account.email == email, Account.is_deactivated == False).first()

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


async def add_picture(db: Session, picture: UploadFile, entity_type: str, entity_id: int) -> bool:
    res = await resize_picture(image_data=picture, target_size=(DEFAULT_PICTURE_WIDTH, DEFAULT_PICTURE_HEIGHT))

    if isinstance(res, bytes):
        if entity_type == 'student':
            query = update(Student).where(Student.student_id == entity_id).values(profile_picture=res)
        elif entity_type == 'teacher':
            query = update(Teacher).where(Teacher.teacher_id == entity_id).values(profile_picture=res)
        elif entity_type == 'course':
            query = update(Course).where(Course.course_id == entity_id).values(home_page_picture=res)
        else:
            return False

        db.execute(query)
        db.commit()

        return True

    return False


async def resize_picture(image_data: UploadFile, target_size: tuple) -> bytes | str:

    try:
        image_data = image_data.file.read()
        image = Image.open(BytesIO(image_data))
        resized_image = image.resize(target_size)
        resized_data = BytesIO()
        resized_image.save(resized_data, format=image.format)

        return resized_data.getvalue()

    except (OSError, UnidentifiedImageError) as e:
        return e


async def email_exists(db: Session, email: str) -> Account | None:
   return db.query(Account).filter(Account.email == email).first()
