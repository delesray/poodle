import pytest
from fastapi.testclient import TestClient
from database.models import Account
from core.security import Token
from api.api_v1.routes.public import login

user = Account(email='dummy@mail.com',
               password='dummypass',
               role='student',
               is_deactivated=False)

token = Token(access_token='valid_token', token_type='bearer')


# def test_login_returns_token_when_correct_credentials(client: TestClient, mocker):
#     mocker.patch('api.api_v1.routes.public.crud_user.try_login', return_value=user)
#     mocker.patch('app.api.api_v1.routes.public.create_access_token', return_value=token)
#
#     login_data = {
#         'username': 'dummy@mail.com',
#         'password': 'dummypass'
#     }
#
#     response = client.post('/login', data=login_data)
#     assert response.status_code == 200
#     assert response.json() == token.dict()

@pytest.mark.asyncio
async def test_login_returns_token_when_correct_credentials(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.try_login', return_value=user)
    mocker.patch('api.api_v1.routes.public.create_access_token', return_value=token)

    login_data = {
        'username': 'dummy@mail.com',
        'password': 'dummypass'
    }

    actual = await login(form_data=login_data, db=None)
    assert actual == token

