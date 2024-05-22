from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.database import Base
from enum import Enum


class Role(Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


class ContentType(Enum):
    video = 'video'
    image = 'image'
    text = 'text'
    quiz = 'quiz'


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(200))
    role: Mapped[Role]

    admin = relationship("Admin", uselist=False, backref="account")
    student = relationship("Student", uselist=False, backref="account")
    teacher = relationship("Teacher", uselist=False, backref="account")


class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[Optional[str]] = mapped_column(String(30))
    linked_in: Mapped[Optional[str]] = mapped_column(String(200))
    profile_picture: Mapped[Optional[bytes]]
    is_deactivated: Mapped[Optional[bool]] = mapped_column(default=False)

    # back_populates is bi-directional, backref is not
    courses: Mapped[List['Course']] = relationship(back_populates="owner")


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    profile_picture: Mapped[Optional[bytes]]
    is_premium: Mapped[Optional[bool]] = mapped_column(default=False)
    is_deactivated: Mapped[Optional[bool]] = mapped_column(default=False)

    """Relationships in SQLAlchemy return query objects to provide flexibility, efficiency, and lazy loading. 
    You need to use methods like all() on the query object to get the actual list of related model objects. 
    This approach helps you manage complex relationships and data retrieval efficiently."""

    # calling student.courses_enrolled should return a query object with all courses the student has enrolled in
    # using all() on that object would retrieve the actual course records
    courses_enrolled: Mapped[List['Course']] = relationship(
        secondary="students_progress",
        back_populates="students_enrolled"
    )
    courses_rated: Mapped[List['Course']] = relationship(
        secondary="students_rating",
        back_populates="students_rated")
    
    sections_visited: Mapped[List['Section']] = relationship(
        secondary="students_sections", back_populates="students_visited")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(250))
    objectives: Mapped[str] = mapped_column(String(250))
    owner_id: Mapped[int] = mapped_column(ForeignKey('teachers.teacher_id'))
    is_premium: Mapped[Optional[bool]] = mapped_column(default=False)
    is_hidden: Mapped[Optional[bool]] = mapped_column(default=False)
    home_page_picture: Mapped[Optional[bytes]] = mapped_column(default=False)
    rating: Mapped[int] = mapped_column(default=0)

    owner: Mapped['Teacher'] = relationship(back_populates="courses")
    students_enrolled: Mapped[List['Student']] = relationship(
        secondary="students_progress",
        back_populates="courses_enrolled"
    )
    students_rated: Mapped[List['Student']] = relationship(
        secondary="students_rating",
        back_populates="courses_rated")
    
    sections: Mapped[List['Section']] = relationship(back_populates="course")
    tags: Mapped['Tag'] = relationship(secondary="courses_tags", back_populates="courses")


class StudentProgress(Base):
    __tablename__ = 'students_progress'

    student_id: Mapped[int] = mapped_column(
        ForeignKey('students.student_id'), primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.id'), primary_key=True)
    progress: Mapped[int] = mapped_column(default=0)


class StudentRating(Base):
    __tablename__ = 'students_rating'

    student_id: Mapped[int] = mapped_column(
        ForeignKey('students.student_id'), primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.id'), primary_key=True)
    rating: Mapped[int] = mapped_column(default=0)


class Section(Base):
    __tablename__ = 'sections'

    section_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(45))
    content: Mapped[Optional[ContentType]]
    description: Mapped[Optional[str]] = mapped_column(String(250))
    external_link: Mapped[Optional[str]] = mapped_column(String(500))
    course_id: Mapped[Optional[int]] = mapped_column(ForeignKey('courses.id'))

    course: Mapped['Course'] = relationship(back_populates="sections")
    students_visited: Mapped[List['Student']] = relationship(
        secondary="students_sections", back_populates="sections_visited")


class StudentsSections(Base):
    __tablename__ = 'students_sections'

    student_id: Mapped[int] = mapped_column(ForeignKey(
        'students.student_id'), primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey(
        'sections.section_id'), primary_key=True)


class Tag(Base):
    __tablename__ = 'tags'

    tag_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45))

    courses = relationship("Course", secondary="courses_tags", back_populates="tags")


class CourseTag(Base):
    __tablename__ = 'courses_tags'

    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tags.tag_id'), primary_key=True)
