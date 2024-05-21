from fastapi import APIRouter
from routes import login, students, teachers

api_router = APIRouter()

api_router.include_router(students.router)
api_router.include_router(login.router)
api_router.include_router(teachers.router)
