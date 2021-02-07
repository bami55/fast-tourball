from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class CustomField(BaseModel):
    machine_name: str
    label: str
    target_type: str
    type: str
    default_value: str
    required: bool
    public: bool
    position: bool

class Lineup(BaseModel):
    name: str
    custom_user_identifier: Optional[str]
    email: str
    custom_fields: str
    user_id: Optional[str]

class Participant(BaseModel):
    name: str
    email: Optional[str]
    custom_user_identifier: Optional[str]
    checked_in: bool
    custom_fields: Optional[str]
    id: int
    user_id: Optional[str]
    created_at: datetime
    lineup: List[]
