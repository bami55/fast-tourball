from pydantic import BaseModel
from typing import Optional

from api.models.ballchasing import Cumulative, GameAverage


class Player(BaseModel):
    platform: str
    id: int
    name: str
    team: str
    cumulative: Optional[Cumulative]
    game_average: Optional[GameAverage]
