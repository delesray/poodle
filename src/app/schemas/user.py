from pydantic import BaseModel, EmailStr
from typing import Annotated, Literal

class AnonymousUser:
    pass

class User(BaseModel):
    email: EmailStr
    password: str
    role: Annotated[str, Literal["teacher", "student"]]
