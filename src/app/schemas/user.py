from pydantic import BaseModel, StringConstraints
from typing import Annotated

class AnonymousUser:
    pass

class User(BaseModel):
    email: str
    password: str
    role: Annotated[str, StringConstraints(pattern=r'^(teacher|student)$')]
