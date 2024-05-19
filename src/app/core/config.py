from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = 'poodle'
    DB_URL: str = Field(default='mysql+pymysql://dummy/poodle_db', json_schema_extra={'env': 'DB_URL'})
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, json_schema_extra={'env': 'ACCESS_TOKEN_EXPIRE_MINUTES'})

    

# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


# settings = get_settings()