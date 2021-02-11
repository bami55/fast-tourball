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
