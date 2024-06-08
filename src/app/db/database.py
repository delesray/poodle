from typing import Annotated
from fastapi import Depends
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
from typing import Generator
from sqlalchemy.orm import Session

Base = declarative_base()


def get_engine_and_session() -> tuple:
    DB_USER = 'user'
    DB_PASS = 'password'
    DB_PORT = 3306
    DB_NAME = 'poodle'
    DB_HOST = 'db'
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def get_db() -> Generator:
    engine, SessionLocal = get_engine_and_session()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    engine, _ = get_engine_and_session()
    if not database_exists(engine.url):
        create_database(engine.url)


dbDep = Annotated[Session | None, Depends(get_db)]
