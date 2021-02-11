from pydantic import BaseModel
from typing import Optional


class CumulativeCore(BaseModel):
    shots: int
    shots_against: int
    goals: int
    goals_against: int
    saves: int
    assists: int
    score: int
    mvp: Optional[int]
    shooting_percentage: float
