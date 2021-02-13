from pydantic import BaseModel
from typing import Optional


class Positioning(BaseModel):
    avg_distance_to_ball: Optional[float]
    avg_distance_to_ball_possession: Optional[float]
    avg_distance_to_ball_no_possession: Optional[float]
    time_defensive_third: Optional[float]
    time_neutral_third: Optional[float]
    time_offensive_third: Optional[float]
    time_defensive_half: Optional[float]
    time_offensive_half: Optional[float]
    time_behind_ball: Optional[float]
    time_infront_ball: Optional[float]
    time_most_back: Optional[float]
    time_most_forward: Optional[float]
    goals_against_while_last_defender: Optional[float]
    time_closest_to_ball: Optional[float]
    time_farthest_from_ball: Optional[float]
    percent_defensive_third: Optional[float]
    percent_offensive_third: Optional[float]
    percent_neutral_third: Optional[float]
    percent_defensive_half: Optional[float]
    percent_offensive_half: Optional[float]
    percent_behind_ball: Optional[float]
    percent_infront_ball: Optional[float]
