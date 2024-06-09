from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()
    # App
    APP_NAME: str = os.environ.get('APP_NAME', 'poodle')
    DEBUG: bool = bool(os.environ.get('DEBUG', False))  # todo future consider the debug modes

    # Database config
    # DB_USER: str = os.environ.get('DB_USER', 'root')
    # DB_PASS: str = os.environ.get('DB_PASS', 'password')
    # DB_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASS}@localhost/poodle?charset=utf8mb4"

    DB_USER: str = os.environ.get('DB_USER', 'root')
    DB_PASS: str = os.environ.get('DB_PASS', 'password')
    DB_PORT: int = 3306
    DB_NAME: str = 'poodle'
    DB_HOST: str = 'localhost'
    DB_URL: str = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    # todo postgresql url

    # Authentication
    ALGORITHM: str = os.environ.get('ALGORITHM', 'RS256')
    ACCESS_TOKEN_EXPIRE_DAYS: int = os.environ.get('ACCESS_TOKEN_EXPIRE_DAYS', 30)
    AUTH_SECRET_KEY: str = os.environ.get('AUTH_SECRET_KEY', 'notfound')

    # Mail
    MAIL_USERNAME: str = os.environ.get('SENDER_EMAIL', 'notfound')
    # MAIL_PASSWORD: str = os.environ.get('MAIL_PASSWORD', 'notfound')

    # model_config = SettingsConfigDict(env_file='dotenv.env', extra='allow')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
