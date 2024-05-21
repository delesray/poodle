import uvicorn
from fastapi import FastAPI
from database import models
from database.database import engine
from api.routes.students import users_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000)
