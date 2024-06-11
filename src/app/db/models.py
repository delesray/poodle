from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.database import Base
from enum import Enum


class Role(Enum):
    admin = 'admin'
    student = 'student'
    teacher = 'teacher'


class ContentType(Enum):
    video = 'video'
    image = 'image'
    text = 'text'
    quiz = 'quiz'


class Status(Enum):
    pending = 1
    active = 2
    declined = 3


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(200))
    role: Mapped[Role]
    is_deactivated: Mapped[Optional[bool]] = mapped_column(server_default='0')

    admin = relationship("Admin", uselist=False, backref="account")
    student = relationship("Student", uselist=False, backref="account")
    teacher = relationship("Teacher", uselist=False, backref="account")

    def __repr__(self):
        return f"<Account(account_id={self.account_id}, email={self.email}, role={self.role.name})>"


class Admin(Base):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)

    def __repr__(self):
        return f"<Admin(admin_id={self.admin_id})>"


class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[Optional[str]] = mapped_column(String(30))
    linked_in: Mapped[Optional[str]] = mapped_column(String(200))
    profile_picture: Mapped[Optional[bytes]]

    courses: Mapped[List['Course']] = relationship(back_populates="owner")

    def __repr__(self):
        return f"<Teacher(teacher_id={self.teacher_id}, first_name={self.first_name}, last_name={self.last_name})>"


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    profile_picture: Mapped[Optional[bytes]]
    is_premium: Mapped[Optional[bool]] = mapped_column(server_default='0')

    courses_enrolled: Mapped[List['Course']] = relationship(
        'Course',
        secondary='students_courses',
        primaryjoin=f"and_(Student.student_id == foreign(StudentCourse.student_id), "
                    f"StudentCourse.status == {Status.active.value})",
        secondaryjoin="Course.course_id == foreign(StudentCourse.course_id)",
        back_populates="students_enrolled"
    )
    courses_rated: Mapped[List['Course']] = relationship(
        secondary="students_ratings",
        back_populates="students_rated")

    sections_visited: Mapped[List['Section']] = relationship(
        secondary="students_sections", back_populates="students_visited")

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, first_name={self.first_name}, last_name={self.last_name})>"


class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(250))
    objectives: Mapped[str] = mapped_column(String(250))
    owner_id: Mapped[int] = mapped_column(ForeignKey('teachers.teacher_id'))
    is_premium: Mapped[Optional[bool]] = mapped_column(server_default='0')
    is_hidden: Mapped[Optional[bool]] = mapped_column(server_default='0')
    home_page_picture: Mapped[Optional[bytes]]
    rating: Mapped[Optional[float]]
    people_rated: Mapped[Optional[int]] = mapped_column(server_default='0')

    owner: Mapped['Teacher'] = relationship(back_populates="courses")
    students_enrolled: Mapped[List['Student']] = relationship(
        secondary="students_courses",
        back_populates="courses_enrolled"
    )
    students_rated: Mapped[List['Student']] = relationship(
        secondary="students_ratings",
        back_populates="courses_rated")

    sections: Mapped[List['Section']] = relationship(back_populates="course")
    tags: Mapped[List['Tag']] = relationship(
        secondary="courses_tags", back_populates="courses")

    def __repr__(self):
        return f"<Course(course_id={self.course_id}, title={self.title}, owner_id={self.owner_id})>"


class StudentCourse(Base):
    __tablename__ = 'students_courses'

    student_id: Mapped[int] = mapped_column(
        ForeignKey('students.student_id'), primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), primary_key=True)
    status: Mapped[int] = mapped_column(
        Integer, server_default=text(str(Status.pending.value)))

    def __repr__(self):
        return f"<StudentCourse(student_id={self.student_id}, course_id={self.course_id})>"


class StudentRating(Base):
    __tablename__ = 'students_ratings'

    student_id: Mapped[int] = mapped_column(
        ForeignKey('students.student_id'), primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), primary_key=True)
    rating: Mapped[float]

    def __repr__(self):
        return f"<StudentRating(student_id={self.student_id}, course_id={self.course_id}, rating={self.rating})>"


class Section(Base):
    __tablename__ = 'sections'

    section_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(45))
    content_type: Mapped[ContentType]
    external_link: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(String(250))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.course_id'))

    course: Mapped['Course'] = relationship(back_populates="sections")
    students_visited: Mapped[List['Student']] = relationship(
        secondary="students_sections", back_populates="sections_visited")

    def __repr__(self):
        return f"<Section(section_id={self.section_id}, title={self.title}, course_id={self.course_id})>"


class StudentSection(Base):
    __tablename__ = 'students_sections'

    student_id: Mapped[int] = mapped_column(ForeignKey(
        'students.student_id'), primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey(
        'sections.section_id'), primary_key=True)

    def __repr__(self):
        return f"<StudentSection(student_id={self.student_id}, section_id={self.section_id})>"


class Tag(Base):
    __tablename__ = 'tags'

    tag_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), unique=True)

    courses: Mapped[List['Course']] = relationship(
        secondary="courses_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag(tag_id={self.tag_id}, name={self.name})>"

    def __str__(self):
        return f'#{self.name}'


class CourseTag(Base):
    __tablename__ = 'courses_tags'

    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tags.tag_id'), primary_key=True)

    def __repr__(self):
        return f"<CourseTag(course_id={self.course_id}, tag_id={self.tag_id})>"
