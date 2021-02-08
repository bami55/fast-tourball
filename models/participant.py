from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional


class CustomField(BaseModel):
    machine_name: Optional[str]
    label: Optional[str]
    target_type: Optional[str]
    type: Optional[str]
    default_value: Optional[str]
    required: Optional[bool]
    public: Optional[bool]
    position: Optional[bool]


class Lineup(BaseModel):
    name: str
    custom_user_identifier: Optional[str]
    email: Optional[str]
    custom_fields: Optional[CustomField]
    user_id: Optional[str]


class Participant(BaseModel):
    name: str
    email: Optional[str]
    custom_user_identifier: Optional[str]
    checked_in: bool
    custom_fields: Optional[CustomField]
    id: str
    user_id: Optional[str]
    created_at: datetime
    lineup: List[Lineup]
