from fastapi.testclient import TestClient
from db.models import Account
from core.security import Token
from schemas.course import CourseInfo


user = Account(email='dummy@mail.com',
               password='dummy pass',
               role='student',
               is_deactivated=False)


token = Token(access_token='valid_token',
              token_type='bearer')


def create_course():
    return CourseInfo(title='title1',
                      description='Test Course',
                      is_premium=False,
                      tags=['tag1', 'tag2'])


def test_login_returns_token_when_correct_credentials(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.try_login', return_value=user)
    mocker.patch('api.api_v1.routes.public.create_access_token', return_value=token)

    login_data = {
        'username': 'dummy@mail.com',
        'password': 'dummy pass'
    }

    response = client.post('/login', data=login_data)
    assert response.status_code == 200
    assert response.json() == token.model_dump()


def test_login_raises_401_when_incorrect_credentials(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.try_login', return_value=None)

    login_data = {
        'username': 'dummy@mail.com',
        'password': 'dummy pass'
    }

    response = client.post('/login', data=login_data)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid credentials'}


def test_get_all_courses_returns_all_courses_if_courses(client: TestClient, mocker):
    courses = [create_course(),
               create_course(),
               create_course()]
    mocker.patch('api.api_v1.routes.public.crud_course.get_all_courses', return_value=courses)

    response = client.get('/courses/')
    assert response.status_code == 200
    response_courses = response.json()

    assert len(response_courses) == len(courses)

    for i, course in enumerate(response_courses):
        expected_course = courses[i]

        assert course['title'] == expected_course.title
        assert course['description'] == expected_course.description
        assert course['is_premium'] == expected_course.is_premium
        assert course['tags'] == expected_course.tags


def test_get_all_courses_returns_empty_list_if_no_courses(client: TestClient, mocker):
    courses = []
    mocker.patch('api.api_v1.routes.public.crud_course.get_all_courses', return_value=courses)

    response = client.get('/courses/')
    assert response.status_code == 200
    assert response.json() == []
