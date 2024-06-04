import io
import pytest
from fastapi.testclient import TestClient
from core.oauth import get_student_required
from db.models import Account, Student
from core.security import Token
from fastapi import status
from main import app

dummy_account = Account(account_id=1,
                        email='dummy@mail.com',
                        password='dummy pass',
                        role='student',
                        is_deactivated=False)

dummy_student = Student(
    student_id=1,
    account=dummy_account,
)

new_student_request = {
    "email": "dummy@mail.com",
    "password": "dummyPass",
    "first_name": "dummyName",
    "last_name": "dummyName"
}

student_response = {
    "first_name": "dummyName",
    "last_name": "dummyName",
    "is_premium": False
}

token = Token(access_token='valid_token',
              token_type='bearer')


@pytest.mark.asyncio
async def test_student_not_authenticated(client: TestClient):

    # store the current dependency override
    original_override = app.dependency_overrides.get(get_student_required)

    # delete it
    if get_student_required in app.dependency_overrides:
        del app.dependency_overrides[get_student_required]

    # execute the test with the original dep
    response = client.get('/students')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'

    # restore the dependency override for the rest of the tests
    if original_override:
        app.dependency_overrides[get_student_required] = original_override


def test_register_returns_409_when_conflict(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=dummy_account)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_register_returns_registered_student_model(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_user.create', return_value=student_response)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == student_response


def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.add_picture', return_value=True)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/students', files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == 'Profile picture successfully uploaded!'


def test_update_profile_picture_invalid_file(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.add_picture', return_value=False)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/students', files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'File is corrupted or media type is not supported'}


def test_view_account_returns_student_account_info(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_student.get_student', return_value=student_response)

    response = client.get('/students')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == student_response
