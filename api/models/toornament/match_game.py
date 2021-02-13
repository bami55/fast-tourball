from pydantic import BaseModel
from typing import List, Optional


class Opponent(BaseModel):
    number: int
    position: int
    result: Optional[str]
    rank: Optional[int]
    forfeit: bool
    score: Optional[int]


class MatchGame(BaseModel):
    status: str
    opponents: List[Opponent]
    number: int
