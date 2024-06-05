import io
import pytest
from fastapi.testclient import TestClient
from core.oauth import get_student_required
from db.models import Account, Student, Course, Teacher, Section
from core.security import Token
from fastapi import status
from main import app
from schemas.course import CourseInfo

dummy_account = Account(account_id=1,
                        email='dummy@mail.com',
                        password='dummy pass',
                        role='student',
                        is_deactivated=False)

dummy_student = Student(
    student_id=1,
    account=dummy_account,
)

dummy_teacher = Teacher(
    teacher_id=2
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

student_updates = {'first_name': 'dummyName',
                   'last_name': 'dummyName'}

dummy_course = {'title': 'dummyTitle', 'course_id': 1}
dummy_section = Section(section_id=1,
                        title='dummyTitle',
                        content_type='video',
                        course_id=dummy_course['course_id'])

dummy_section_dto = {'section_id': dummy_section.section_id,
                     'title': 'dummyTitle',
                     'content_type': 'video',
                     'description': 'dummyDescription',
                     'external_link': None,
                     'course_id': dummy_course['course_id']
                     }

dummy_student_course_info = {'course_id': 1,
                             'title': 'DummyCourse',
                             'description': 'DummyDesc',
                             'objectives': 'DummyObjectives',
                             'owner_id': dummy_teacher.teacher_id,
                             'owner_name': 'dummyName',
                             'is_premium': False,
                             'overall_rating': 0.0,
                             'your_rating': 0.0,
                             'your_progress': 0.0,
                             }


def create_course():
    return CourseInfo(title='title1',
                      description='Test Course',
                      is_premium=False,
                      tags=['tag1', 'tag2'])


def override_get_current_student():
    return Student(is_premium=True)


@pytest.mark.asyncio
async def test_student_not_authenticated(client: TestClient):
    original_override = app.dependency_overrides.get(get_student_required)

    if get_student_required in app.dependency_overrides:
        del app.dependency_overrides[get_student_required]

    response = client.get('/students')
    data = response.json()

    assert response.status_code == 401
    assert data['detail'] == 'Not authenticated'

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


def test_edit_account_returns_student_account_info(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_student.edit_account', return_value=student_response)

    response = client.put('/students', json=student_updates)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == student_response


def test_change_pass_returns_204_when_success(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.utils.change_pass_raise', return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_user.change_password', return_value=None)

    pass_updates = {'old_password': 'pass1',
                    'new_password': 'pass1',
                    'confirm_password': 'pass2'}
    response = client.patch('/students', json=pass_updates)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_view_my_courses_returns_list_with_courses(client: TestClient, mocker):
    courses = [create_course(),
               create_course(),
               create_course()]

    mocker.patch('api.api_v1.routes.students.crud_student.get_my_courses', return_value=courses)

    response = client.get('/students/courses')

    assert response.status_code == status.HTTP_200_OK
    response_courses = response.json()

    assert len(response_courses) == len(courses)

    for i, course in enumerate(response_courses):
        expected_course = courses[i]

        assert course['title'] == expected_course.title
        assert course['description'] == expected_course.description
        assert course['is_premium'] == expected_course.is_premium
        assert course['tags'] == expected_course.tags


def test_view_my_courses_returns_empty_list_when_no_courses(client: TestClient, mocker):
    courses = []

    mocker.patch('api.api_v1.routes.students.crud_student.get_my_courses', return_value=courses)

    response = client.get('/students/courses')

    assert response.status_code == status.HTTP_200_OK
    response_courses = response.json()

    assert len(response_courses) == len(courses)


def test_view_pending_courses_returns_list_with_courses(client: TestClient, mocker):
    courses = [create_course(),
               create_course(),
               create_course()]

    mocker.patch('api.api_v1.routes.students.crud_student.view_pending_requests', return_value=courses)

    response = client.get('/students/courses/pending')

    assert response.status_code == status.HTTP_200_OK
    response_courses = response.json()

    assert len(response_courses) == len(courses)

    for i, course in enumerate(response_courses):
        expected_course = courses[i]

        assert course['title'] == expected_course.title
        assert course['description'] == expected_course.description
        assert course['is_premium'] == expected_course.is_premium
        assert course['tags'] == expected_course.tags


def test_view_pending_courses_returns_empty_list_when_no_courses(client: TestClient, mocker):
    courses = []

    mocker.patch('api.api_v1.routes.students.crud_student.get_my_courses', return_value=courses)

    response = client.get('/students/courses')

    assert response.status_code == status.HTTP_200_OK
    response_courses = response.json()

    assert len(response_courses) == len(courses)


def test_view_course_raises_404_when_no_such_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id', return_value=None)
    course_id = 1

    response = client.get(f'/students/courses/{course_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such course'


def test_view_course_raises_409_when_not_enrolled(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled', return_value=False)
    course_id = 1

    response = client.get(f'/students/courses/{course_id}')
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data['detail'] == 'You have to enroll in this course to view details about it'


def test_view_course_returns_course_info(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=True)
    mocker.patch('api.api_v1.routes.students.crud_student.get_course_information',
                 return_value=dummy_student_course_info)
    course_id = 1

    response = client.get(f'/students/courses/{course_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == dummy_student_course_info


def test_view_course_section_raises_404_when_no_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=None)

    course_id = 1
    section_id = 1

    response = client.get(f'/students/courses/{course_id}/sections/{section_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such course'


def test_view_course_section_raises_404_when_no_section(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_section.get_section_by_id',
                 return_value=None)

    course_id = 1
    section_id = 1

    response = client.get(f'/students/courses/{course_id}/sections/{section_id}')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such Section'


def test_view_course_section_raises_403_when_not_enrolled(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_section.get_section_by_id',
                 return_value=dummy_section)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=False)

    course_id = 1
    section_id = 1

    response = client.get(f'/students/courses/{course_id}/sections/{section_id}')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'You have to enroll in this course to view details about it'


def test_view_course_section_returns_section(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_section.get_section_by_id',
                 return_value=dummy_section)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=True)
    mocker.patch('api.api_v1.routes.students.crud_section.add_student',
                 return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_section.transfer_object',
                 return_value=dummy_section_dto)

    course_id = 1
    section_id = 1

    response = client.get(f'/students/courses/{course_id}/sections/{section_id}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == dummy_section_dto


def test_subscribe_for_course_raises_404_when_no_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=None)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/subscription')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such course'


def test_subscribe_for_course_returns_correct_msg_when_already_enrolled(client: TestClient, mocker):
    course = Course(title='Test Course')
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=True)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/subscription')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == (f'You are already subscribed for course {course.title}. '
                    'Click on <View Course> or <View Course Section> to access its content')


def test_subscribe_for_course_raises_403_when_premium_required(client: TestClient, mocker):
    course = Course(title='Test Course', is_premium=True)
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=False)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/subscription')
    data = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data['detail'] == 'Upgrade to premium to enroll in this course'


def test_subscribe_for_course_raises_400_when_premium_limit_reached(client: TestClient, mocker):
    course = Course(title='Test Course', is_premium=True)
    client.app.dependency_overrides[get_student_required] = override_get_current_student
    course_limit_reached = 6

    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id', return_value=course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled', return_value=False)
    mocker.patch('api.api_v1.routes.students.crud_student.get_premium_courses_count', return_value=course_limit_reached)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/subscription')

    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['detail'] == 'Premium courses limit reached'

    client.app.dependency_overrides[get_student_required] = lambda: dummy_student


def test_subscribe_for_course_returns_correct_msg_when_success(client: TestClient, mocker):
    course = Course(title='Test Course')
    msg = 'Pending approval'

    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=False)
    mocker.patch('api.api_v1.routes.students.crud_student.add_pending_student_request',
                 return_value=None)
    mocker.patch('api.api_v1.routes.students.crud_student.send_notification',
                 return_value=msg)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/subscription')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data == 'Pending approval'


def test_unsubscribe_from_course_raises_404_when_no_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=None)

    course_id = 1

    response = client.delete(f'/students/courses/{course_id}/subscription')
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such course'


def test_unsubscribe_from_course_returns_204_when_success(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_student.unsubscribe_from_course',
                 return_value=None)

    course_id = 1

    response = client.delete(f'/students/courses/{course_id}/subscription')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_rate_course_raises_404_when_no_course(client: TestClient, mocker):
    student_rating = 5

    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=None)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/rating', json={'rating': student_rating})
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'No such course'


def test_rate_course_raises_409_when_not_enrolled(client: TestClient, mocker):
    student_rating = 5
    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=False)

    course_id = 1

    response = client.post(f'/students/courses/{course_id}/rating', json={'rating': student_rating})
    data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert data['detail'] == 'You have to enroll in this course to rate it'


def test_rate_course_returns_correct_response_when_success(client: TestClient, mocker):
    student_rating = 5
    rate_response = {'course': 'someCourse',
                     'rating': student_rating}

    mocker.patch('api.api_v1.routes.students.crud_course.get_course_by_id',
                 return_value=dummy_course)
    mocker.patch('api.api_v1.routes.students.crud_student.is_student_enrolled',
                 return_value=True)
    mocker.patch('api.api_v1.routes.students.crud_student.update_add_student_rating',
                 return_value=rate_response)

    course_id = 1


    response = client.post(f'/students/courses/{course_id}/rating', json={'rating': student_rating})
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data == rate_response
