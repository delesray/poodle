from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# from src.app.core.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db" # connect_args={"check_same_thread": False}
# SQLALCHEMY_DATABASE_URL = settings.DB_URL

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@localhost/poodle?charset=utf8mb4"

# factory that can create new database connections
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


def get_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    if not database_exists(engine.url):
        create_database(engine.url)


# todo curr dependancy mock change
dbDep = Annotated[Session | None, Depends(get_db)]
