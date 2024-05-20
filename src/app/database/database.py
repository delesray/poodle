import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.hidden import USER, PASS
#from src.app.core.config import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db" # connect_args={"check_same_thread": False}
#SQLALCHEMY_DATABASE_URL = settings.DB_URL

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASS}@localhost/poodle?charset=utf8mb4"
# MARIADB EXAMPLE: "mysql+pymysql://scott:tiger@localhost/test?charset=utf8mb4"

# factory that can create new database connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)   # argument is needed only for SQLite. It's not needed for other databases.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()  # The declarative_base() function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0)

# to create all tables:
# Base.metadata.create_all(engine)

def get_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()