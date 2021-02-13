from pydantic import BaseModel
from typing import List, Optional

from api.models.ballchasing import Cumulative, GameAverage, Player


class Team(BaseModel):
    name: str
    players: List[Player]
    cumulative: Optional[Cumulative]
    game_average: Optional[GameAverage]
