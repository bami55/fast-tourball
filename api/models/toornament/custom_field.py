from pydantic import BaseModel
from typing import Optional


class CustomField(BaseModel):
    machine_name: Optional[str]
    label: Optional[str]
    target_type: Optional[str]
    type: Optional[str]
    default_value: Optional[str]
    required: Optional[bool]
    public: Optional[bool]
    position: Optional[bool]
