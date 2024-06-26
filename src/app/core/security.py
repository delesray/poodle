from pydantic import BaseModel
from typing import Union
from datetime import timedelta, datetime
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/login", auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    role: str


async def create_access_token(data: TokenData) -> Token:
    to_encode = dict(data)
    expire = datetime.now() + \
        timedelta(days=int(os.environ['ACCESS_TOKEN_EXPIRE_DAYS']))
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, os.environ['AUTH_SECRET_KEY'],
                             os.environ['ALGORITHM'])
    return Token(access_token=encoded_jwt, token_type='bearer')


async def is_token_exp_valid(exp: str) -> bool:
    exp_datetime = datetime.strptime(exp, '%Y-%m-%d %H:%M:%S')
    return exp_datetime > datetime.now()


async def verify_token_access(token: str) -> Union[TokenData, str]:
    try:
        payload = jwt.decode(
            token, os.environ['AUTH_SECRET_KEY'], algorithms=os.environ['ALGORITHM'])
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp_at: str = payload.get("expire")

        if not await is_token_exp_valid(exp_at):
            raise ExpiredSignatureError()

        token_data = TokenData(email=email, role=role)
        return token_data

    except ExpiredSignatureError:
        return "Token has expired. Please log in again"

    except JWTError:
        return "Invalid token"
