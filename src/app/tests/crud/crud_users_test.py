from unittest.mock import Mock

import pytest
from fastapi import HTTPException, status
from tests import dummies
from crud import crud_user


@pytest.mark.asyncio
async def test_get_specific_user_or_raise_404_if_no_such_account(db, test_db):
    with pytest.raises(HTTPException) as e:
        await crud_user.get_specific_user_or_raise_404(
            db=db, user_id=dummies.NON_EXISTING_ID, role='student'
        )

    assert e.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_specific_user_or_raise_404_if_no_match(db, test_db):
    _, student = await dummies.create_dummy_student(db)
    account, admin = await dummies.create_dummy_admin(db)

    with pytest.raises(HTTPException) as e:
        await crud_user.get_specific_user_or_raise_404(
            db=db, user_id=admin.admin_id, role='student'
        )

    assert e.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_specific_user_or_raise_404_happy_case(db, test_db):
    _, student = await dummies.create_dummy_student(db)
    account, teacher = await dummies.create_dummy_teacher(db)

    res_teacher = await crud_user.get_specific_user_or_raise_404(
        db=db, user_id=account.account_id, role='teacher'
    )

    assert res_teacher.teacher_id == teacher.teacher_id


@pytest.mark.asyncio
async def test_get_create_user_raises_409(db, test_db, mocker):
    account, admin = await dummies.create_dummy_admin(db)
    mock_user = Mock()
    mock_user.email = dummies.dummy_user.email
    mock_user.password = dummies.dummy_user.password
    mock_user.get_type = lambda: 'admin'

    with pytest.raises(HTTPException) as e:
        await crud_user.create_user(db=db, user=mock_user)

    assert e.value.status_code == status.HTTP_409_CONFLICT
