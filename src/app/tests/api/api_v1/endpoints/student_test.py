import io
from fastapi.testclient import TestClient
from db.models import Account, Student
from core.security import Token
from fastapi import status

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

new_student_response = {
    "first_name": "dummyName",
    "last_name": "dummyName",
    "is_premium": False
}

token = Token(access_token='valid_token',
              token_type='bearer')


def test_register_returns_409_when_conflict(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=dummy_account)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_register_returns_registered_student_model(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_user.create', return_value=new_student_response)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == new_student_response


def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.add_picture', return_value=True)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/students', files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == 'Profile picture successfully uploaded!'
