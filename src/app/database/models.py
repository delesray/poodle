from sqlalchemy import Boolean, Column, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.app.database import Base


# -------------------- DB MODELS with Column --------------------
class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(200))

    # 1:1 relationship with Admin, Student, Teacher
    # calling student.account would return the Account record of the corresponding Student
    admin = relationship("Admin", uselist=False, backref="account")
    student = relationship("Student", uselist=False, backref="account")
    teacher = relationship("Teacher", uselist=False, backref="account")


class Admin(Base):
    __tablename__ = "admins"
    admin_id = Column(Integer, ForeignKey(
        'accounts.account_id'), primary_key=True)


class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    profile_picture = Column(LargeBinary, nullable=True)
    phone_number = Column(String(30), nullable=True)
    linked_in = Column(String(200), nullable=True)
    is_deactivated = Column(Boolean, default=False, nullable=True)

    # back_populates is bi-directional, backref is not
    courses = relationship("Course", back_populates="teacher")


class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, ForeignKey(
        'accounts.account_id'), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    profile_picture = Column(LargeBinary, nullable=True)
    is_premium = Column(Boolean, default=False, nullable=True)
    is_deactivated = Column(Boolean, default=False, nullable=True)

    """Relationships in SQLAlchemy return query objects to provide flexibility, efficiency, and lazy loading. 
    You need to use methods like all() on the query object to get the actual list of related model objects. 
    This approach helps you manage complex relationships and data retrieval efficiently."""

    # calling student.courses_enrolled should return a query object with all courses the student has enrolled in
    # using all() on that object would retrieve the actual course records
    courses_enrolled = relationship("Course", secondary="students_progress")
    courses_rated = relationship("Course", secondary="students_rating")
    sections_visited = relationship("Section", secondary="students_sections")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    description = Column(String)
    objectives = Column(String)
    owner_id = Column(Integer, ForeignKey('teachers.id'))
    is_premium = Column(Boolean, default=False, nullable=True)
    is_hidden = Column(Boolean, default=False, nullable=True)
    home_page_picture = Column(LargeBinary, nullable=True)
    rating = Column(Integer, default=0)

    owner = relationship("Teacher", back_populates="courses")

    students_enrolled = relationship(
        "Student", secondary="students_progress")
    students_rated = relationship(
        "Student", secondary="students_rating")
    sections = relationship("Section", back_populates="course")
    tags = relationship("Tag", secondary="courses_tags")


class StudentProgress(Base):
    __tablename__ = 'students_progress'
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    progress = Column(Integer, default=0)


class StudentRating(Base):
    __tablename__ = 'students_rating'
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    rating = Column(Integer, default=0)


class Section(Base):
    __tablename__ = 'sections'

    section_id = Column(Integer, primary_key=True)
    title = Column(String(45), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(String(45), nullable=True)
    external_link = Column(String(200), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    course = relationship("Course", back_populates="sections")
    students_visited = relationship("Student", secondary="students_sections")


class StudentsSections(Base):
    __tablename__ = 'students_sections'

    student_id = Column(Integer, ForeignKey(
        'students.student_id'), primary_key=True)
    section_id = Column(Integer, ForeignKey(
        'sections.section_id'), primary_key=True)


class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    courses = relationship("Course", secondary="courses_tags")


class CourseTag(Base):
    __tablename__ = 'courses_tags'

    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.tag_id'), primary_key=True)

# -------------------- DB MODELS with Mapped --------------------


class Account(Base):
    __tablename__ = "accounts"
    account_id = Mapped[int] = mapped_column(primary_key=True)
    email = Mapped[str] = mapped_column(String(30))
    password = Mapped[str] = mapped_column(String(200))

    admin = relationship("Admin", uselist=False, backref="account")
    student = relationship("Student", uselist=False, backref="account")
    teacher = relationship("Teacher", uselist=False, backref="account")