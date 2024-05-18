from fastapi import APIRouter
from ...core.oauth import UserAuthDep

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=UserAuthDep,
    responses={404: {"description": "Not found"}},
)