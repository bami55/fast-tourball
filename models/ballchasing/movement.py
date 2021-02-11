from pydantic import BaseModel
from typing import Optional


class Movement(BaseModel):
    avg_speed: Optional[float]
    total_distance: Optional[float]
    time_supersonic_speed: Optional[float]
    time_boost_speed: Optional[float]
    time_slow_speed: Optional[float]
    time_ground: Optional[float]
    time_low_air: Optional[float]
    time_high_air: Optional[float]
    time_powerslide: Optional[float]
    count_powerslide: Optional[float]
    avg_powerslide_duration: Optional[float]
    avg_speed_percentage: Optional[float]
    percent_slow_speed: Optional[float]
    percent_boost_speed: Optional[float]
    percent_supersonic_speed: Optional[float]
    percent_ground: Optional[float]
    percent_low_air: Optional[float]
    percent_high_air: Optional[float]
