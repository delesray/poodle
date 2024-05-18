from pydantic import BaseModel
from typing import Union
from datetime import timedelta, datetime
from jose import jwt, JWTError, ExpiredSignatureError
import secrets
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
SECRET_KEY = secrets.token_urlsafe(32)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    is_admin: bool


def create_access_token(data: TokenData) -> Token:
    to_encode = dict(data)
    expire = datetime.now() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return Token(access_token=encoded_jwt, token_type='bearer')


def is_token_exp_valid(exp: str) -> bool:
    exp_datetime = datetime.strptime(exp, '%Y-%m-%d %H:%M:%S')
    return exp_datetime > datetime.now()


def verify_token_access(token: str) -> Union[TokenData, str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin")
        exp_at: str = payload.get("expire")

        if not is_token_exp_valid(exp_at):
            raise ExpiredSignatureError()

        token_data = TokenData(username=username, is_admin=is_admin)
        return token_data

    except ExpiredSignatureError:
        return "Token has expired. Please log in again"

    except JWTError:
        return "Invalid token"
