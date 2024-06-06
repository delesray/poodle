import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from tests import dummies
from api.api_v1.routes.admins import switch_user_activation

ROUTER_PREFIX = 'admins'


def test_switch_user_activation_raise_404_when_no_user(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.get_user_by_id_deactivated_also', return_value=None)

    response = client.patch(f'{ROUTER_PREFIX}/accounts/{dummies.NON_EXISTING_ID}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'No such user'}


@pytest.mark.asyncio
async def test_2_switch_user_activation_raise_404_when_no_user(mocker):
    """Different approach that enters inside the function in debugging"""
    mocker.patch('api.api_v1.routes.public.crud_user.get_user_by_id_deactivated_also', return_value=None)

    with pytest.raises(HTTPException) as e:
        await switch_user_activation(None, dummies.dummy_admin, dummies.NON_EXISTING_ID)

    assert e.value.status_code == status.HTTP_404_NOT_FOUND


def test_switch_user_activation_raise_409_when_same_user(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.get_user_by_id_deactivated_also', return_value=dummies.dummy_user)

    response = client.patch(f'{ROUTER_PREFIX}/accounts/{dummies.dummy_admin.admin_id}')

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_2_switch_user_activation_raise_409_when_same_user(client: TestClient, mocker):
    mocker.patch('api.api_v1.routes.public.crud_user.get_user_by_id_deactivated_also', return_value=dummies.dummy_user)

    with pytest.raises(HTTPException) as e:
        await switch_user_activation(
            None, dummies.dummy_admin, dummies.dummy_user.account_id
        )

    assert e.value.status_code == status.HTTP_409_CONFLICT