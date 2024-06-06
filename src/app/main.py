import uvicorn
from fastapi import FastAPI
from db import models
from db import database
from db.database import get_engine_and_session
from api.api_v1.api import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == '__main__':
    database.create_db()
    engine = get_engine_and_session()[0]
    models.Base.metadata.create_all(bind=engine)
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
