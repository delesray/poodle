from io import BytesIO
from sqlalchemy import update
from sqlalchemy.orm import Session
from schemas.user import UserChangePassword
from schemas.teacher import TeacherCreate, TeacherSchema
from schemas.student import StudentCreate, StudentResponseModel
from database.models import Account, Teacher, Student
from core.hashing import hash_pass
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, UploadFile
from typing import Union, Type
from core import hashing
from PIL import Image, UnidentifiedImageError

DEFAULT_PICTURE_WIDTH = 400
DEFAULT_PICTURE_HEIGHT = 400


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


class StudentFactory():
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


async def create(db: Session, user_schema: Union[StudentCreate, TeacherCreate]) -> Union[TeacherSchema, StudentResponseModel]:
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


async def add_picture(db: Session, picture: UploadFile, student_id: int):
    res = await resize_picture(image_data=picture, target_size=(DEFAULT_PICTURE_WIDTH, DEFAULT_PICTURE_HEIGHT))

    if isinstance(res, bytes):
        query = update(Student).where(Student.student_id == student_id)
        query = query.values(profile_picture=res)

        db.execute(query)
        db.commit()

        return True

    return False


async def resize_picture(image_data: UploadFile, target_size: tuple) -> bytes | str:
    """
    Resizes an image from a BinaryIO object to the specified target size (width, height)
    """
    try:
        # Read the entire file content into a bytes object
        image_data = image_data.file.read()

        # Open the image from the bytes object
        image = Image.open(BytesIO(image_data))
        # Resize the image
        resized_image = image.resize(target_size)

        # Create a BytesIO object to store the resized image (in-memory)
        resized_data = BytesIO()
        # Save in the original format
        resized_image.save(resized_data, format=image.format)

        return resized_data.getvalue()

    except (OSError, UnidentifiedImageError) as e:
        return e
