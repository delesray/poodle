from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_db
from crud import crud_user
from core.security import create_access_token, TokenData
from sqlalchemy.orm import Session


router = APIRouter()


@router.post('/login', include_in_schema=False)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    """
    Logs a user.

    **Parameters:**
    - `form_data` (OAuth2PasswordRequestForm): the class dependency that implements the OAuth2 password flow
    - `db` (Session): The SQLAlchemy database session.

    **Returns**: a Token object (JWT)

    **Raises**: HTTPException 401, if the user's credentials are incorrect.

    """
    user = await crud_user.try_login(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await create_access_token(
        TokenData(email=user.email, role=user.role))
    return token
