import uvicorn
from fastapi import FastAPI
from db import models
# from db.db import engine, create_db
from db import database
from api.api_v1.api import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == '__main__':
    database.create_db()
    models.Base.metadata.create_all(bind=database.engine)
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
