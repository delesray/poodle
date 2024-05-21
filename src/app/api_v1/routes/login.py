from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database.database import DbSession
from crud import crud_user
from core.security import create_access_token, TokenData


router = APIRouter(tags=['login'])


@router.post('/login', include_in_schema=False)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """
    - Logs the user, if username and password are correct
    - Returns access Token
    """
    user = crud_user.try_login(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        TokenData(email=user.email, role=user.role))
    return token
