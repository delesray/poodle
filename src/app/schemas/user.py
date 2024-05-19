from pydantic import BaseModel

class AnonymousUser:
    pass

class User(BaseModel):
    email: str
    password: str
    role: str
