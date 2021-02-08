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


@app.get("/tournaments/{tournament_id}/groups")
def get_groups(tournament_id):
    data = tournaments.get_groups(tournament_id)
    return {"groups": data}


@app.get("/tournaments/{tournament_id}/stages")
def get_stages(tournament_id):
    data = tournaments.get_stages(tournament_id)
    return {"stages": data}


@app.get("/tournaments/{tournament_id}/matches")
def get_matches(tournament_id):
    data = tournaments.get_matches(tournament_id)
    return {"matches": data}


@app.get("/tournaments/{tournament_id}/matches/{match_id}/games")
def get_matches(tournament_id, match_id):
    data = tournaments.get_match_games(tournament_id, match_id)
    return {"match_games": data}
