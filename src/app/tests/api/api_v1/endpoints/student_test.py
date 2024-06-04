import io
import pytest
from fastapi.testclient import TestClient
from db.models import Account
from core.security import Token

account = Account(email='dummy@mail.com',
                  password='dummy pass',
                  role='student',
                  is_deactivated=False)

new_student_request = {
    "email": "dummy@mail.com",
    "password": "dummyPass",
    "first_name": "dummyName",
    "last_name": "dummyName"
}

new_student_response = {
    "first_name": "dummyName",
    "last_name": "dummyName",
    "is_premium": False
}

token = Token(access_token='valid_token',
              token_type='bearer')


@pytest.fixture
def mock_student():
    student = account.student
    return student


def test_register_returns_409_when_conflict(client: TestClient, mocker, test_db, db):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=account)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == 409
    assert response.json() == {'detail': 'Email already registered'}


def test_register_returns_registered_student_model(client: TestClient, mocker, test_db, db):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_user.create', return_value=new_student_response)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == 201
    assert response.json() == new_student_response

# todo fix
def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker, test_db):
    mocker.patch('api.api_v1.routes.students.crud_user.add_picture', return_value=True)

    test_image_content = b'Test image content'
    test_image = io.BytesIO(test_image_content)

    response = client.post(f'/students',
                           headers={"Authorization": f"Bearer {token}"},
                           files={"image": ("test_image.jpg", test_image, "image/jpeg")})

    assert response.status_code == 201
    assert response.json() == "Profile picture successfully uploaded!"
