from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


@app.get("/")
def read_root():
    return {"greetings": "Welcome to LearnCodeOnline.in"}
