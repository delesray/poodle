from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from crud.crud_user import create_user
from schemas.user import User
from core.oauth import AdminAuthDep
from sqlalchemy.orm import Session
from database.database import get_db

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@users_router.post('/register', status_code=201)
async def register_user(db: Annotated[Session, Depends(get_db)], user: User):
    """
    TODO
    """
    result = await create_user(db, user)

    # if not isinstance(result, int):
    #     raise HTTPException(status_code=400, detail=result.msg)

    return f"User with ID: {result} registered"
