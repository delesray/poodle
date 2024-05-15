from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


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


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
