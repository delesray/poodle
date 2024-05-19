from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from src.app.database.database import get_db
from sqlalchemy.orm import Session
from src.app.schemas.user import User
from src.app.database.models import Account
from src.app.crud.crud_user import create_user
from src.app.crud.crud_teacher import update, create_new_course
from src.app.schemas.teacher import Teacher, TeacherEditInfo
from src.app.schemas.course import Course
from src.app.core.oauth import TeacherAuthDep 

teachers_router = APIRouter(prefix='/teachers', tags=['teachers'])

teachers_router.post("/register")
async def register_teacher(teacher: User, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(Account).filter(Account.email == teacher.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
        
    return await create_user(db, teacher)


@teachers_router.put('/')
async def update_info(teacher: TeacherEditInfo, existing_teacher: TeacherAuthDep):
    return await update(existing_teacher, teacher)


@teachers_router.post("/course")
async def create_course(new_course: Course, existing_teacher: TeacherAuthDep):
    return await create_new_course(new_course, existing_teacher)


