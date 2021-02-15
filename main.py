from fastapi import FastAPI
from pydantic import BaseModel

import os

from api import Toornament, Ballchasing

app = FastAPI()

tournaments = Toornament()
ballchasing = Ballchasing()


@app.get("/")
def read_root():
    return {
        "greetings": "Welcome to LearnCodeOnline.in",
        "debug": os.environ['DEBUG'],
        "test": "check deploy."
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


@app.get("/replay/groups/{group_id}")
def get_replay_group(group_id):
    data = ballchasing.get_group(group_id)
    return {"replay_group": data}


@app.get("/replay/get_group_children/{group_id}")
def get_group_children(group_id):
    data = ballchasing.get_group_children(group_id)
    for day in data:
        for player in day.players:
            print(player.name)
    return {"replay_group_children": data}


@app.get("/init_db/{tournament_id}/{group_id}")
def init_db(tournament_id, group_id):
    tournaments.init_db(tournament_id)
    ballchasing.init_db(group_id)
    return {"init_db": "success!"}
