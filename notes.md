# ORM mode

Pydantic models define the data structure for your API responses and requests.
orm_mode=True instructs Pydantic to use ORM mode, which tells it how to convert SQLAlchemy model instances to dictionaries based on the Pydantic model definition.
Here's how you set it up:

```Python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserInDB(BaseModel):
    id: int
    name: str

class UserOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True  # Configure orm_mode here

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(...)):
    user = db.get(UserInDB, user_id)  # Fetch user from database
    return user  # Pydantic will automatically convert to UserOut
```

In this example, the UserOut model defines the expected structure of the response data. Setting orm_mode=True in its configuration tells Pydantic to convert the retrieved UserInDB instance (from SQLAlchemy) to a dictionary matching the UserOut structure before returning it as a JSON response.
