from pydantic import BaseModel

from models.ballchasing import CumulativeCore, Boost, Demo, Movement, Positioning


class Cumulative(BaseModel):
    games: int
    wins: int
    win_percentage: float
    play_duration: int
    core: CumulativeCore
    boost: Boost
    movement: Movement
    positioning: Positioning
    demo: Demo
