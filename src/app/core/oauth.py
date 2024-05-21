from enum import Enum
from fastapi import HTTPException, Depends
from typing import Annotated
from core.security import verify_token_access, oauth2_scheme, oauth2_scheme_optional, TokenData
from schemas.user import AnonymousUser, User
from crud.crud_user import exists
from database.models import Role
from database.database import get_db
from sqlalchemy.orm import Session


async def get_admin_required(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(token)
    if not user.role == Role.admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user


async def get_teacher_required(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(token)
    if not user.role == Role.teacher:
        raise HTTPException(status_code=403, detail="Teacher required")
    return user


async def get_student_required(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(db, token)
    if not user.role == Role.student:
        raise HTTPException(status_code=403, detail="Student required")
    return user


async def get_user_optional(token: Annotated[str, Depends(oauth2_scheme_optional)]):
    if not token:
        return AnonymousUser()
    return await get_current_user(token)


async def get_current_user(db, token):
    token_data = await verify_token_access(token)

    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=400, detail=token_data)

    user = await exists(db=db, email=token_data.email)
    
    if not user:
        raise HTTPException(status_code=404, detail="No such user")

    return user


AdminAuthDep = Annotated[User, Depends(get_admin_required)]
TeacherAuthDep = Annotated[User, Depends(get_teacher_required)]
StudentAuthDep = Annotated[User, Depends(get_student_required)]
OptionalUser = Annotated[User | AnonymousUser, Depends(get_user_optional)]
