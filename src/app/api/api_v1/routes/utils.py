from fastapi import HTTPException
from core.hashing import verify_password


async def change_pass_raise(student, pass_update):
    if not pass_update.old_password != pass_update.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")
    if not verify_password(pass_update.old_password, student.password):
        raise HTTPException(status_code=401, detail="Current password does not match")
    if not pass_update.new_password == pass_update.confirm_password:
        raise HTTPException(status_code=400, detail="New password does not match")