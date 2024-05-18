from passlib.context import CryptContext

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_pass(password: str) -> str:
    return pass_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pass_context.verify(plain_password, hashed_password)
