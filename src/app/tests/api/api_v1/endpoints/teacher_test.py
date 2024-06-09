import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from schemas.course import CourseSectionsTags, CourseUpdate, CourseBase
from schemas.section import SectionBase, SectionUpdate
from schemas.tag import TagBase
from schemas.student import StudentResponseModel
from core.security import Token
from db.models import Account, Teacher, Course, Section, CourseTag, Student
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
    first_name="dummyName",
    last_name="dummyName",
    account=dummy_account
)
dummy_student_account = Account(account_id=2, email='dummy_student@mail.com')
dummy_student = Student(
    student_id=2,
    account=dummy_student_account
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

dummy_course = Course(
    course_id=1,
    title="Test Course",
    description="A test course",
    objectives="Test objectives",
    owner_id=1,
    is_premium=False,
    is_hidden=False,
    home_page_picture=None,
    rating=None,
    people_rated=0
)

dummy_coursebase = CourseBase(
        course_id=1,
        title="Test Course",
        description="A test course",
        objectives="Test objectives",
        owner_id=1,
        owner_names=f"{dummy_teacher.first_name} {dummy_teacher.last_name}",
        is_premium=False,
        rating=None,
        people_rated=0
    )

dummy_section = Section(
    section_id=1,
    title="Test Section",
    content_type="video",
    external_link="http://example.com",
    description="A test section",
    course_id=1
)

def create_dummy_sectionbase(title, content_type, external_link, description):
    return  SectionBase(
        section_id=1,
        title=title,
        content_type=content_type,
        external_link=external_link,
        description=description,
        course_id=1   
)

dummy_updates_course = CourseUpdate(
    title="Updated Course",
    description="Updated description",
    objectives="Updated objectives"
)

dummy_updates_section = SectionUpdate(
    title="Updated Section",
    content_type="text",
    external_link="http://updated.com",
    description="Updated description"
)

dummy_tagbase = TagBase(
    tag_id=1,
    name="Test Tag"
)

dummy_course_tag = CourseTag(
    course_id=1,
    tag_id=1
)

dummy_course_report = {
            "course_id": dummy_course.course_id,
            "title": dummy_course.title,
            "students": [{
                "student_info": StudentResponseModel.from_query(first_name="dummyName", last_name="dummyName"),
                "progress": "50.00"
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
    mocker.patch('api.api_v1.routes.teachers.crud_course.course_exists', return_value=False)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.make_course', return_value=course_response)

    response = client.post('/teachers/courses', json=course_request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == course_response
    

def test_create_course_returns_409_when_course_exists(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.course_exists', return_value=True)

    response = client.post('/teachers/courses', json=course_request)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Course with such title already exists'}
    
    
def test_update_course_home_page_picture_returns_successful_msg(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_user.add_picture', return_value=True)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers/courses/home-page-picture?course_id=1', files=files)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == 'Home page picture successfully uploaded!'


def test_update_course_home_page_picture_invalid_file(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_user.add_picture', return_value=False)

    test_file = io.BytesIO(b"fake image data")
    files = {'file': ('test_image.png', test_file, 'image/png')}

    response = client.post('/teachers/courses/home-page-picture?course_id=1', files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'File is corrupted or media type is not supported'}
    

def test_view_pending_requests_returns_pending_requests(client: TestClient, mocker):
    pending_requests = [
        {"course": "Course 1", "requested_by": "student1@mail.com"},
        {"course": "Course 2", "requested_by": "student2@mail.com"}
    ]
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.view_pending_requests', return_value=pending_requests)

    response = client.get('/teachers/courses/pending')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == pending_requests


def test_get_courses_returns_list_of_courses(client: TestClient, mocker):
    dummy_courses = [dummy_coursebase]
    
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.get_my_courses', return_value=dummy_courses)

    response = client.get('/teachers/courses')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "course_id": dummy_coursebase.course_id,
            "title": dummy_coursebase.title,
            "description": dummy_coursebase.description,
            "objectives": dummy_coursebase.objectives,
            "owner_id": dummy_coursebase.owner_id,
            "owner_names": f'{dummy_teacher.first_name} {dummy_teacher.last_name}',
            "is_premium": dummy_coursebase.is_premium,
            "rating": dummy_coursebase.rating,
            "people_rated": dummy_coursebase.people_rated,
        }
    ]    

def test_view_course_by_id_returns_CourseSectionsTags_object(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.get_entire_course', 
                 return_value=CourseSectionsTags(course=dummy_coursebase, tags=[], sections=[]))

    response = client.get('/teachers/courses/1')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "course": {
            "course_id": dummy_coursebase.course_id,
            "title": dummy_coursebase.title,
            "description": dummy_coursebase.description,
            "objectives": dummy_coursebase.objectives,
            "owner_id": dummy_coursebase.owner_id,
            "owner_names": f'{dummy_teacher.first_name} {dummy_teacher.last_name}',
            "is_premium": dummy_coursebase.is_premium,
            "rating": dummy_coursebase.rating,
            "people_rated": dummy_coursebase.people_rated,
        },
        "tags": [],
        "sections": []
    }
    
def test_view_course_by_id_invalid_sort(client: TestClient, mocker):
    response = client.get('/teachers/courses/1?sort=invalid')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid sort parameter'}
    
def test_view_course_by_id_invalid_sort_by(client: TestClient, mocker):
    response = client.get('/teachers/courses/1?sort_by=invalid')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid sort_by parameter'}
    
def test_view_course_by_id_access_denied(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(False, "You do not have permission to access this course"))

    response = client.get('/teachers/courses/1')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'You do not have permission to access this course'}
    
def test_update_course_info_returns_updated_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.edit_course_info', return_value=dummy_coursebase)

    response = client.put('/teachers/courses/1', json=dummy_updates_course.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
            "course_id": dummy_coursebase.course_id,
            "title": dummy_coursebase.title,
            "description": dummy_coursebase.description,
            "objectives": dummy_coursebase.objectives,
            "owner_id": dummy_coursebase.owner_id,
            "owner_names": f'{dummy_teacher.first_name} {dummy_teacher.last_name}',
            "is_premium": dummy_coursebase.is_premium,
            "rating": dummy_coursebase.rating,
            "people_rated": dummy_coursebase.people_rated,
        }
    
def test_update_course_info_access_denied(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(False, "You do not have permission to access this course"))

    response = client.put('/teachers/courses/1', json=dummy_updates_course.model_dump())

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'You do not have permission to access this course'}
    
def test_update_section_returns_updated_section(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_section.get_section_by_id', return_value=dummy_section)
    mocker.patch('api.api_v1.routes.teachers.crud_section.update_section_info', 
                 return_value=create_dummy_sectionbase(
                     title="Updated Section",
                     content_type="text",
                     external_link="http://updated.com",
                     description="Updated description"
                    )
    )

    response = client.put('/teachers/courses/1/sections/1', json=dummy_updates_section.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "section_id": dummy_section.section_id,
        "title": dummy_updates_section.title,
        "content_type": dummy_updates_section.content_type,
        "external_link": dummy_updates_section.external_link,
        "description": dummy_updates_section.description,
        "course_id": dummy_section.course_id
    }

    
def test_update_section_not_found(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_section.get_section_by_id', return_value=None)

    response = client.put('/teachers/courses/1/sections/999', json=dummy_updates_section.model_dump())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Section not found'}
    
    
def test_add_sections_returns_list_of_created_sections(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_section.create_sections', 
                 return_value=[create_dummy_sectionbase(
                     title = "New Section",
                     content_type =  "text",
                     external_link =  "http://new.com",
                     description = "New description"
                    )]
    )

    new_section = {
        "title": "New Section",
        "content_type": "text",
        "external_link": "http://new.com",
        "description": "New description"
    }

    response = client.post('/teachers/courses/1/sections', json=[new_section])

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == [
        {
            "section_id": dummy_section.section_id,
            "title": new_section['title'],
            "content_type": new_section['content_type'],
            "external_link": new_section['external_link'],
            "description": new_section['description'],
            "course_id": dummy_section.course_id
        }
    ]
    
def test_remove_section_removes_section_from_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_section.get_section_by_id', return_value=dummy_section)
    mocker.patch('api.api_v1.routes.teachers.crud_section.delete_section', return_value=None)

    response = client.delete('/teachers/courses/1/sections/1')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ''
    
def test_add_tags_returns_list_of_tags_and_list_of_duplicated_tagIds(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_tag.create_tags', return_value={"created": [dummy_tagbase], "duplicated_tags_ids": [1]})

    new_tag = {
        "name": "Test Tag"
    }

    response = client.post('/teachers/courses/1/tags', json=[new_tag])

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "created": [{"tag_id": dummy_tagbase.tag_id, "name": new_tag['name']}],
        "duplicated_tags_ids": [1]
    }
    
    
def test_add_tags_access_denied(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(False, "You do not have permission to access this course"))

    new_tag = {
        "name": "New Tag"
    }

    response = client.post('/teachers/courses/1/tags', json=[new_tag])

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'You do not have permission to access this course'}
    
    
def test_remove_tag_removes_tag_from_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_tag.course_has_tag', return_value=dummy_course_tag)
    mocker.patch('api.api_v1.routes.teachers.crud_tag.delete_tag_from_course', return_value=None)
    mocker.patch('api.api_v1.routes.teachers.crud_tag.check_tag_associations', return_value=0)
    mocker.patch('api.api_v1.routes.teachers.crud_tag.delete_tag', return_value=None)

    response = client.delete('/teachers/courses/1/tags/1')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ''
    

def test_remove_tag_not_found(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_tag.course_has_tag', return_value=None)

    response = client.delete('/teachers/courses/1/tags/999')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Tag with ID:999 not associated with course ID:1'}
    
    
def test_deactivate_course(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))
    mocker.patch('api.api_v1.routes.teachers.crud_course.hide_course', return_value=None)

    dummy_course.students_enrolled = []

    response = client.patch('/teachers/courses/1/deactivate')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ''
    
    
def test_deactivate_course_with_enrolled_students(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_course.get_course_common_info', return_value=dummy_course)
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.validate_course_access', return_value=(True, "OK"))

    dummy_course.students_enrolled = [dummy_student]

    response = client.patch('/teachers/courses/1/deactivate')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Cannot deactivate a course with enrolled students'}
    
    
def test_generate_courses_reports_returns_list_of_courses_with_student_progresses(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.teachers.crud_teacher.get_courses_reports', return_value=dummy_course_report)

    response = client.get('/teachers/reports?min_progress=50.0')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
            "course_id": dummy_course.course_id,
            "title": dummy_course.title,
            "students": [{
                "student_info": {"first_name": "dummyName",
                                  "last_name": "dummyName",
                                  "is_premium": False
                                },
                "progress": "50.00"
            }]
        }
    
def test_generate_courses_reports_invalid_min_progress(client: TestClient):
    response = client.get('/teachers/reports?min_progress=invalid&sort=asc')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid min_progress parameter'}
    
    
def test_generate_courses_reports_invalid_sort(client: TestClient):
    response = client.get('/teachers/reports?min_progress=0.0&sort=invalid')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Invalid sort parameter'}
    
    

