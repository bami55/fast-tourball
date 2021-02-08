from pydantic import BaseModel
from typing import Dict


class Stage(BaseModel):
    id: str
    number: int
    name: str
    type: str
    closed: bool
    settings: Dict
