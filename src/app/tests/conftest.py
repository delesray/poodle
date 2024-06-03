import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker

from db.database import get_db, Base
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db() -> Session:
    """
    Provides a SQLAlchemy session for testing purposes.

    This fixture returns a session connected to an in-memory SQLite db.
    It's intended for use in tests that require db access but should not
    affect the production db.

    Returns:
        Session: A SQLAlchemy session object.
    """
    return TestingSessionLocal()


SQLite_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLite_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def test_db():
    """
    Sets up and tears down an in-memory SQLite db for testing.

    This fixture creates all tables in the Base metadata before tests run and
    drops them after tests complete. It ensures that tests run with a clean
    db every time.

    Yields:
        None: This fixture doesn't return any value.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """
    Overrides the 'get_db' dependency for testing.

    This function replaces the standard db session with a session connected
    to the in-memory SQLite db. It's used to override the app's dependency
    during tests to ensure isolation from the production db.

    Yields:
        Generator[Session, None, None]: A generator yielding the test db session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
