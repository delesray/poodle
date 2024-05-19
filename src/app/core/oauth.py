from enum import Enum
from fastapi import HTTPException, Depends
from typing import Annotated
from core.security import verify_token_access, oauth2_scheme, oauth2_scheme_optional, TokenData
from schemas.user import AnonymousUser, User
from crud.crud_user import find_by_email

class Role(Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'


def get_admin_required(token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token)
    if not user.role == Role.admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return user


def get_teacher_required(token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token)
    if not user.role == Role.teacher:
        raise HTTPException(status_code=403, detail="Teacher required")
    return user


def get_student_required(token: Annotated[str, Depends(oauth2_scheme)]):
    user = get_current_user(token)
    if not user.role == Role.student:
        raise HTTPException(status_code=403, detail="Student required")
    return user


# def get_user_required(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
#     return get_current_user(token)


def get_user_optional(token: Annotated[str, Depends(oauth2_scheme_optional)]) -> User | AnonymousUser:
    if not token:
        return AnonymousUser()
    return get_current_user(token)


def get_current_user(token):
    token_data = verify_token_access(token)

    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=400, detail=token_data)

    user = find_by_email(token_data.email)
    
    if not user:
        raise HTTPException(status_code=404, detail="No such user")

    return user


AdminAuthDep = Annotated[User, Depends(get_admin_required)]
TeacherAuthDep = Annotated[User, Depends(get_teacher_required)]
StudentAuthDep = Annotated[User, Depends(get_student_required)]
OptionalUser = Annotated[User | AnonymousUser, Depends(get_user_optional)]
