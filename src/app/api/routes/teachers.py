from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from src.app.database.database import get_db
from sqlalchemy.orm import Session
from src.app.schemas.user import User
from src.app.database.models import Account
from src.app.crud.crud_user import create_user

teachers_router = APIRouter(prefix='/teachers', tags=['teachers'])

teachers_router.post("/register/teacher")
async def register_teacher(teacher: User, db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(Account).filter(Account.email == teacher.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
        
    return await create_user(db, teacher)

