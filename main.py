from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import datetime
import os
import traceback

from api import database, Toornament, Ballchasing

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tournaments = Toornament()
ballchasing = Ballchasing()


@app.get("/")
def read_root():
    return {
        "dot_env_check": os.environ['DEBUG'],
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
async def init_db(tournament_id, group_id, background_tasks: BackgroundTasks):
    try:
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT NEXTVAL('background_task_id_seq')")
                background_task_id = cursor.fetchone()[0]
                values = (background_task_id, 'api request', datetime.datetime.now())
                cursor.execute("INSERT INTO background_tasks (id, status, created_at) VALUES (%s, %s, %s)", values)
    except:
        st = traceback.format_exc()
        return {
            "status": "DBの接続に失敗しました。",
            "error": st
        }

    background_tasks.add_task(tournaments.init_db, tournament_id, background_task_id)
    background_tasks.add_task(ballchasing.init_db, group_id, background_task_id)
    return {"status": "DBの初期化を開始しました。"}


@app.get("/scores_by_days")
def get_scores_by_days():
    try:
        scores = ballchasing.get_scores_by_days()
        return {"scores": scores}
    except:
        st = traceback.format_exc()
        return {"error": st}


@app.get("/scores_all")
def get_scores_all():
    try:
        scores = ballchasing.get_scores_all()
        return {"scores": scores}
    except:
        st = traceback.format_exc()
        return {"error": st}


@app.get("/teams")
def get_teams():
    try:
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM teams ORDER BY id")
                columns = [column[0] for column in cursor.description]
                teams = []
                for row in cursor.fetchall():
                    teams.append(dict(zip(columns, row)))
                return {"teams": teams}
    except:
        st = traceback.format_exc()
        return {"error": st}


@app.get("/streaming_match")
def get_streaming_match():
    try:
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    SELECT
                        sm.position,
                        sm.team_id,
                        t.name as team_name
                    FROM streaming_match sm
                    INNER JOIN teams t
                        ON sm.team_id = t.id
                    ORDER BY
                        position
                """
                cursor.execute(sql)
                columns = [column[0] for column in cursor.description]
                teams = []
                for row in cursor.fetchall():
                    teams.append(dict(zip(columns, row)))
                return {"teams": teams}
    except:
        st = traceback.format_exc()
        return {"error": st}


@app.post("/streaming_match")
def set_streaming_match(teams: list):
    try:
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                for team in teams:
                    cursor.execute("UPDATE streaming_match SET team_id = %s WHERE position = %s", (team['id'], team['position']))
        return {"status": "success"}
    except:
        st = traceback.format_exc()
        return {
            "status": "error",
            "error": st
        }
