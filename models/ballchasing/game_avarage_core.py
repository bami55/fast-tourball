from pydantic import BaseModel
from typing import Optional


class GameAverageCore(BaseModel):
    shots: float
    shots_against: float
    goals: float
    goals_against: float
    saves: float
    assists: float
    score: float
    mvp: Optional[int]
    shooting_percentage: float
