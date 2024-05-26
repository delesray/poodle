import sqlalchemy
from sqlalchemy import create_engine
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
