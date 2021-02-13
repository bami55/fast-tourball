from datetime import datetime
from pydantic import BaseModel
from typing import List
from models.ballchasing import Player, Team


class Creator(BaseModel):
    steam_id: int
    name: str
    profile_url: str
    avatar: str
    avatar_full: str
    avatar_medium: str


class ReplayGroup(BaseModel):
    id: str
    link: str
    name: str
    created: datetime
    status: str
    player_identification: str
    team_identification: str
    shared: bool
    creator: Creator
    players: List[Player]
    teams: List[Team]
