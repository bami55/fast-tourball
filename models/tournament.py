from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class Logo(BaseModel):
    logo_small: Optional[str]
    logo_medium: Optional[str]
    logo_large: Optional[str]
    original: Optional[str]

class Tournament(BaseModel):
    id: int
    discipline: str
    name: str
    full_name: Optional[str]
    status: str
    scheduled_date_start: Optional[date]
    scheduled_date_end: Optional[date]
    timezone: Optional[str]
    online: bool
    public: bool
    location: Optional[str]
    country: Optional[str]
    size: Optional[int]
    platforms: List[str]
    logo: Optional[Logo]
    registration_enabled: bool
    registration_opening_datetime: Optional[datetime]
    registration_closing_datetime: Optional[datetime]
