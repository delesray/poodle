from fastapi import APIRouter
from api.api_v1.routes import students, teachers
from api.api_v1.routes import public

api_router = APIRouter()

api_router.include_router(students.router)
api_router.include_router(public.router)
api_router.include_router(teachers.router)
