from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from database.database import get_db
from sqlalchemy.orm import Session
from core.oauth import TeacherAuthDep, StudentAuthDep
from typing import Union

router = APIRouter(prefix='/courses', tags=['courses'])

@router.get("/")
async def get_courses(db: Annotated[Session, Depends(get_db)], user: Union[StudentAuthDep, TeacherAuthDep]):
    pass


@router.get("/{course_id}")
async def get_course_by_id(
    db: Annotated[Session, Depends(get_db)],
    course_id: int,
    user:  Union[StudentAuthDep, TeacherAuthDep],
    sort: str | None = None,
    sort_by: str | None = None):
    
    # if sort and sort.lower() not in ['asc', 'desc']:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Invalid sort parameter"
    #     )

    # if sort_by and sort_by.lower() not in ['section_id', 'title']:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Invalid sort_by parameter"
    #     )
        
    # course = await get_course_by_id(db, course_id)
    # if not course:
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"Course #ID:{course_id} does not exist"
    #     )
    pass

    