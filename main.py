from fastapi import FastAPI
from pydantic import BaseModel

import os

from app.toornament import Toornament

app = FastAPI()
tournaments = Toornament()


@app.get("/")
def read_root():
    return {
        "greetings": "Welcome to LearnCodeOnline.in",
        "debug": os.environ['DEBUG']
    }


@app.get("/tournaments")
def get_tournaments():
    data = tournaments.get_tournaments()
    return {"tournaments": data}


@app.get("/tournaments/{tournament_id}/participants")
def get_participants(tournament_id):
    data = tournaments.get_participants(tournament_id)
    return {"participants": data}

