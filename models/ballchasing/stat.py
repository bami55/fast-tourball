from pydantic import BaseModel


class Boost(BaseModel):
    amount_collected: float
    amount_stolen: float
    amount_collected_big: float
    amount_stolen_big: float
    amount_collected_small: float
    amount_stolen_small: float
    count_collected_big: float
    count_stolen_big: float
    count_collected_small: float
    count_stolen_small: float
    time_zero_boost: float
    percent_zero_boost: float
    time_full_boost: float
    percent_full_boost: float
    amount_overfill: float
    amount_overfill_stolen: float
    amount_used_while_supersonic: float
    time_boost_0_25: float
    time_boost_25_50: float
    time_boost_50_75: float
    time_boost_75_100: float


class Core(BaseModel):
    shots: float
    shots_against: float
    goals: float
    goals_against: float
    saves: float
    assists: float
    score: float
    shooting_percentage: float


class Demo(BaseModel):
    inflicted: float
    taken: float


class Movement(BaseModel):
    avg_speed: float
    total_distance: float
    time_supersonic_speed: float
    time_boost_speed: float
    time_slow_speed: float
    time_ground: float
    time_low_air: float
    time_high_air: float
    time_powerslide: float
    count_powerslide: float
    avg_powerslide_duration: float
    avg_speed_percentage: float
    percent_slow_speed: float
    percent_boost_speed: float
    percent_supersonic_speed: float
    percent_ground: float
    percent_low_air: float
    percent_high_air: float


class Positioning(BaseModel):
    avg_distance_to_ball: float
    avg_distance_to_ball_possession: float
    avg_distance_to_ball_no_possession: float
    time_defensive_third: float
    time_neutral_third: float
    time_offensive_third: float
    time_defensive_half: float
    time_offensive_half: float
    time_behind_ball: float
    time_infront_ball: float
    time_most_back: float
    time_most_forward: float
    goals_against_while_last_defender: float
    time_closest_to_ball: float
    time_farthest_from_ball: float
    percent_defensive_third: float
    percent_offensive_third: float
    percent_neutral_third: float
    percent_defensive_half: float
    percent_offensive_half: float
    percent_behind_ball: float
    percent_infront_ball: float


class Stat(BaseModel):
    games: int
    wins: int
    win_percentage: float
    play_duration: int
    core: Core
    boost: Boost
    movement: Movement
    positioning: Positioning
    demo: Demo
