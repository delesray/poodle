import uvicorn
from fastapi import FastAPI
from database import models
from database.database import engine
from api_v1.api import api_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api_router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
