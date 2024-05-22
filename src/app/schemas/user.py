from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Literal

class AnonymousUser:
    pass

class User(BaseModel):
    email: EmailStr
    password: str
    role: Annotated[str, Literal["teacher", "student"]]


class UserChangePassword(BaseModel):
    old_password: Annotated[str, StringConstraints(min_length=4)] = None
    new_password: Annotated[str, StringConstraints(min_length=4)] = None
    confirm_password: Annotated[str, StringConstraints(min_length=4)] = None
