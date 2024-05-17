from sqlalchemy import Boolean, Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship
from src.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


"""
One-to-One Relationship
By using the joined-table inheritance strategy, 
each record in the students or teachers table will correspond to a 
single record in the users table, ensuring a one-to-one relationship.
"""


class Student(User):
    __tablename__ = "students"
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }


class Teacher(User):
    __tablename__ = "teachers"
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    linkedin_account = Column(String, unique=True, index=True, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }


# TEST DB MODELS

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(200))


class Admin(Base):
    __tablename__ = "admins"
    admin_id = Column(Integer, ForeignKey('accounts.account_id'), primary_key=True)

class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, ForeignKey('accounts.account_id'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)
    is_premium = Column(Boolean, default=False)
    is_deactivated = Column(Boolean, default=False)

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, ForeignKey('accounts.account_id'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)
    phone_number = Column(String(30), nullable=True)
    linked_in = Column(String(200), nullable=True)
    is_deactivated = Column(Boolean, default=False)