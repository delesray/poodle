import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker
from core.oauth import get_student_required, get_admin_required, get_teacher_required
from db.database import get_db, Base
from main import app
from tests.api.api_v1.endpoints.student_test import dummy_student
from tests.api.api_v1.endpoints.teacher_test import dummy_teacher
from tests import dummies


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='function')
def db() -> Session:
    """
    This fixture returns a session connected to an in-memory SQLite db.
    It's intended for use in tests that require db access but should not
    affect the production db.
    """

    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = lambda: None
app.dependency_overrides[get_student_required] = lambda: dummy_student
app.dependency_overrides[get_teacher_required] = lambda: dummy_teacher
app.dependency_overrides[get_admin_required] = lambda: dummies.get_mock_admin()
