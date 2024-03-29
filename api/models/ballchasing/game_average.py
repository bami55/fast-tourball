from pydantic import BaseModel

from api.models.ballchasing import GameAverageCore, Boost, Demo, Movement, Positioning


class GameAverage(BaseModel):
    core: GameAverageCore
    boost: Boost
    movement: Movement
    positioning: Positioning
    demo: Demo
