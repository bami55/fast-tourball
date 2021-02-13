from pydantic import BaseModel


class Demo(BaseModel):
    inflicted: float
    taken: float
