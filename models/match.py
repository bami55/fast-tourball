from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

from models.custom_field import CustomField


class Participant(BaseModel):
    id: str
    name: str
    custom_user_identifier: Optional[str]
    custom_fields: Optional[CustomField]


class Opponent(BaseModel):
    number: int
    position: int
    result: Optional[str]
    rank: Optional[int]
    forfeit: bool
    score: Optional[int]
    participant: Optional[Participant]


class Match(BaseModel):
    scheduled_datetime: Optional[datetime]
    public_note: Optional[str]
    private_note: Optional[str]
    id: str
    status: str
    stage_id: str
    group_id: str
    round_id: Optional[str]
    number: int
    type: str
    settings: Dict
    played_at: Optional[datetime]
    report_closed: bool
    opponents: List[Opponent]
