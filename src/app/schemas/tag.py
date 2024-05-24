from pydantic import BaseModel, StringConstraints
from typing import Annotated


class TagBase(BaseModel):
    tag_id: int | None = None
    name: Annotated[str, StringConstraints(min_length=1)] = None
    
    
    

