from enum import Enum
from fastapi import HTTPException, Depends, status
from typing import Annotated
from core.security import verify_token_access, oauth2_scheme, oauth2_scheme_optional, TokenData
from schemas.user import AnonymousUser, User
from crud.crud_user import exists
from database.models import Account, Role, Student, Teacher, Admin
from database.database import get_db
from sqlalchemy.orm import Session
from database.models import Account


async def get_admin_required(
        db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> Admin:
    user = await get_current_user(db, token)
    if not user.role == Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user.admin


async def get_teacher_required(
        db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> Teacher:
    user = await get_current_user(db, token)
    if not user.role == Role.teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher required")
    return user.teacher


async def get_student_required(
        db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> Student:
    user: Account = await get_current_user(db, token)
    if not user.role == Role.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student required")
    return user.student


# async def get_user_optional(token: Annotated[str, Depends(oauth2_scheme)]):
#     if not token:
#         return AnonymousUser()
#     return await get_current_user(token)


async def get_current_user(db: Session, token) -> Account:
    token_data = await verify_token_access(token)

    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=token_data)

    user = await exists(db=db, email=token_data.email)

    if not user:
        raise HTTPException(status_code=404, detail="No such user")

    return user


AdminAuthDep = Annotated[Admin, Depends(get_admin_required)]
TeacherAuthDep = Annotated[Teacher, Depends(get_teacher_required)]
StudentAuthDep = Annotated[Student, Depends(get_student_required)]
# OptionalUser = Annotated[Account | AnonymousUser, Depends(get_user_optional)]
