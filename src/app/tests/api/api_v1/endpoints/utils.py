import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db.models import Account, Student
from api.api_v1.routes.utils import change_pass_raise
from fastapi import status, HTTPException
from schemas.user import UserChangePassword
from core.hashing import hash_pass


async def create_dummy_student(db: Session) -> tuple[Account, Student]:
    account_id = 1
    account = Account(
        account_id=account_id,
        email='s@s.com',
        password=hash_pass('pass'),
        role='student',
    )
    student = Student(
        student_id=account_id,
        first_name='Dummy',
        last_name='Student'
    )
    db.add_all([account, student])
    db.commit()
    return account, student


@pytest.mark.asyncio
async def test_change_pass_raise_400_if_new_pass_same_as_old_pass(client: TestClient, db):
    account, student = await create_dummy_student(db)
    pass_updates = UserChangePassword(old_password='pass1',
                                      new_password='pass1',
                                      confirm_password='pass2')

    with pytest.raises(HTTPException) as exc_info:
        await change_pass_raise(account, pass_updates)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "New password must be different"


@pytest.mark.asyncio
async def test_change_pass_raise_401_if_current_pass_does_not_match(client: TestClient, db):
    account, student = await create_dummy_student(db)
    pass_updates = UserChangePassword(old_password='pass1',
                                      new_password='pass3',
                                      confirm_password='pass2')

    with pytest.raises(HTTPException) as exc_info:
        await change_pass_raise(account, pass_updates)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Current password does not match"


@pytest.mark.asyncio
async def test_change_pass_raise_400_if_new_password_does_not_match(client: TestClient, db):
    account, student = await create_dummy_student(db)
    pass_updates = UserChangePassword(old_password='pass',
                                      new_password='pass3',
                                      confirm_password='pass2')

    with pytest.raises(HTTPException) as exc_info:
        await change_pass_raise(account, pass_updates)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "New password does not match"
