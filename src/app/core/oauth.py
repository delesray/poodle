from fastapi import HTTPException, Depends
from typing import Annotated
from src.app.core.security import verify_token_access, oauth2_scheme, oauth2_scheme_optional, TokenData
from app.schemas.user import AnonymousUser, User


def get_admin_required(token: Annotated[str, Depends(oauth2_scheme)]):
    admin = get_current_user(token)
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return admin


def get_user_required(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    return get_current_user(token)


def get_user_optional(token: Annotated[str, Depends(oauth2_scheme_optional)]) -> User | AnonymousUser:
    if not token:
        return AnonymousUser()
    return get_current_user(token)


def get_current_user(token):
    token_data = verify_token_access(token)

    
    if not isinstance(token_data, TokenData):
        raise HTTPException(status_code=400, detail=token_data)

    user = find_by_username(token_data.username)
    
    if not user:
        raise HTTPException(status_code=404, detail="No such user")

    return user


UserAuthDep = Annotated[User, Depends(get_user_required)]
AdminAuthDep = Annotated[User, Depends(get_admin_required)]
OptionalUser = Annotated[User | AnonymousUser, Depends(get_user_optional)]