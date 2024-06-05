import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from schemas.teacher import TeacherSchema, TeacherCreate
from core.security import Token
from db.models import Account, Teacher
from fastapi import status
from main import app
from core.oauth import get_teacher_required

dummy_account = Account(account_id=1,
                  email='dummy@mail.com',
                  password='dummy pass',
                  role='teacher',
                  is_deactivated=False)


dummy_teacher = Teacher(
    teacher_id=1,
    account=dummy_account,
)

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

token = Token(access_token='valid_token',
              token_type='bearer')


course_request = {
    "title": "New Course",
    "description": "Course description",
    "objectives": "Course objectives",
    "is_premium": True,
    "tags": [{"name": "Tag1"}, {"name": "Tag2"}],
    "sections": [{
        "title": "Section 1",
        "content_type": "video", 
        "external_link": "http://example.com",
        "description": "Section description"
    }]
}

course_response = {
    "course": {
        "course_id": 1,
        "title": "New Course",
        "description": "Course description",
        "objectives": "Course objectives",
        "owner_id": 1,
        "owner_names": "Teacher Name",
        "is_premium": True,
        "rating": None,
        "people_rated": 0
    },
    "tags": [
        {"tag_id": 1, "name": "Tag1"},
        {"tag_id": 2, "name": "Tag2"}
    ],
    "sections": [{
        "section_id": 1,
        "title": "Section 1",
        "content_type": "video",  
        "external_link": "http://example.com",
        "description": "Section description",
        "course_id": 1
    }]
}

@pytest.mark.asyncio
async def test_teacher_not_authenticated(client: TestClient):

    # store the current dependency override
    original_override = app.dependency_overrides.get(get_teacher_required)

    # delete it
    if get_teacher_required in app.dependency_overrides:
        del app.dependency_overrides[get_teacher_required]

    # execute the test with the original dep
    response = client.get('/teachers')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'

    # restore the dependency override for the rest of the tests
    if original_override:
        app.dependency_overrides[get_teacher_required] = original_override


def test_register_teacher_returns_registered_teacher_model(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_user.email_exists', return_value=None)
    mocker.patch('crud.crud_user.create', return_value=teacher_response)

    response = client.post('/teachers/register', json=teacher_request)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == teacher_response
    

def test_register_teacher_returns_409_when_email_exists(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_user.email_exists', return_value=dummy_account)

    response = client.post('/teachers/register', json=teacher_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_register_teacher_returns_400_when_account_deactivated(client: TestClient, mocker):
    account_deactivate = Account(
                      account_id=1,
                      email='dummy@mail.com',
                      password='dummy pass',
                      role='teacher',
                      is_deactivated=True)
    
    mocker.patch('api.api_v1.routes.teachers.crud_user.email_exists', return_value=account_deactivate)
    
    response = client.post('/teachers/register', json=teacher_request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Account with this email is deactivated'}
    

def test_update_profile_picture_returns_successful_msg(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_user.add_picture', return_value=True)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers', files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == 'Profile picture successfully uploaded!'


def test_update_profile_picture_invalid_file(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_user.add_picture', return_value=False)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers', files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'File is corrupted or media type is not supported'}


def test_view_account_returns_teacher_account_info(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.get_info', return_value=teacher_response)

    response = client.get('/teachers')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == teacher_response
    

def test_update_account_returns_updated_teacher_info(client: TestClient, mocker):
    update_request = {
    "first_name": "newFirstName",
    "last_name": "newLastName",
    "phone_number": "1234567890",
    "linked_in": "newLinkedInProfile"
}

    update_response = {
    "teacher_id": 1,
    "email": "dummy@mail.com",
    "first_name": "newFirstName",
    "last_name": "newLastName",
    "phone_number": "1234567890",
    "linked_in": "newLinkedInProfile"
}
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.edit_account', return_value=dummy_teacher)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.get_info', return_value=update_response)

    response = client.put('/teachers', json=update_request)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == update_response    


def test_create_course_returns_created_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.course_exists', return_value=False)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.make_course', return_value=course_response)

    response = client.post('/teachers/courses', json=course_request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == course_response
    

def test_create_course_returns_409_when_course_exists(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.course_exists', return_value=True)

    response = client.post('/teachers/courses', json=course_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Course with such title already exists'}