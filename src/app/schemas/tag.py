from pydantic import BaseModel, StringConstraints
from typing import Annotated


class Tag(BaseModel):
    tag_id: int
    name: Annotated[str, StringConstraints(min_length=1)] = None
