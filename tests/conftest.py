import pytest
from fastapi.testclient import TestClient
from src.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
