from pydantic import BaseModel
from typing import Dict


class Group(BaseModel):
    id: str
    stage_id: str
    number: int
    name: str
    closed: bool
    settings: Dict
