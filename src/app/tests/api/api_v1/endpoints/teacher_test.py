import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from schemas.teacher import TeacherSchema, TeacherCreate
from core.security import Token
from db.models import Account
from fastapi import status

account = Account(email='dummy@mail.com',
                  password='dummy pass',
                  role='student',
                  is_deactivated=False)

teacher_request = {
    "email": "dummy@mail.com",
    "password": "dummyPass",
    "first_name": "dummyName",
    "last_name": "dummyName"
}

teacher_response = {
    "teacher_id": 1,
    "email": "dummy@mail.com",
    "first_name": "dummyName",
    "last_name": "dummyName",
    "phone_number": None,
    "linked_in": None
}

def test_register_teacher_returns_registered_teacher_model(client: TestClient, mocker):
    mocker.patch('crud.crud_user.email_exists', return_value=None)
    mocker.patch('crud.crud_user.create', return_value=teacher_response)

    response = client.post('/teachers/register', json=teacher_request)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == teacher_response
    

def test_register_teacher_returns_409_when_email_exists(client: TestClient, mocker):
    mocker.patch('crud.crud_user.email_exists', return_value=account)

    response = client.post('/students/register', json=teacher_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_register_teacher_returns_400_when_account_deactivated(client: TestClient, mocker):
    account_deactivate = Account(email='dummy@mail.com',
                      password='dummy pass',
                      role='teacher',
                      is_deactivated=True)
    
    mocker.patch('crud.crud_user.email_exists', return_value=account_deactivate)
    
    response = client.post('/teachers/register', json=teacher_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Account with this email is deactivated'}
    

def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker):
    mocker.patch('crud.crud_user.add_picture', return_value=True)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers', files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == 'Profile picture successfully uploaded!'


def test_update_profile_picture_invalid_file(client: TestClient, mocker):
    mocker.patch('crud.crud_user.add_picture', return_value=False)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers', files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'File is corrupted or media type is not supported'}


def test_view_account_returns_teacher_account_info(client: TestClient, mocker):
    mocker.patch('crud.crud_teacher.get_info', return_value=teacher_response)

    response = client.get('/teachers')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == teacher_response

    
