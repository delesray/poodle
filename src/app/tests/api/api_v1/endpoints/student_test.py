from fastapi.testclient import TestClient
from db.models import Account, Student
from core.security import Token


account = Account(email='dummy@mail.com',
                  password='dummy pass',
                  role='student',
                  is_deactivated=False)

student = Student(student_id=1,
                  first_name='DummyFirstName',
                  last_name='DummyLastName')

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
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=account)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == 409
    assert response.json() == {'detail': 'Email already registered'}


def test_register_returns_registered_student_model(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_user.exists', return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_user.create', return_value=new_student_response)

    response = client.post('/students/register', json=new_student_request)

    assert response.status_code == 201
    assert response.json() == new_student_response


def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker):
    pass
