import datetime
import json
import requests
import traceback

from psycopg2 import extras

from api import settings, database
from api.models.toornament import Tournament, Participant, Group, Stage, Match, MatchGame


class Toornament:

    BASE_URL = 'https://api.toornament.com/organizer/v2'
    SCOPE = [
        'organizer:view',
        'organizer:admin',
        'organizer:participant',
        'organizer:result',
    ]

    access_token = None
    db = None

    def __init__(self, *args, **kwargs):
        self.db = kwargs.get('db')
        self.auth()

    def auth(self):
        """アクセス認証
        """

        url = 'https://api.toornament.com/oauth/v2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'scope': ' '.join(self.SCOPE),
        }
        r = requests.post(url, data=data)
        data = r.json()
        self.access_token = data['access_token']

    def send_request(self, url, headers={}, method=settings.REQUEST_METHOD['get']):
        """リクエスト送信

        Args:
            url (str): URL
            headers (dict): Header情報
            method (string): Method

        Returns:
            Response: レスポンス
        """

        request_url = self.BASE_URL + url
        base_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Api-Key': settings.API_KEY
        }
        req_headers = {**base_headers, **headers}

        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=req_headers)

    def get_tournaments(self):
        """トーナメントデータ取得

        Returns:
            List[Response]: トーナメントデータ
        """

        url = '/tournaments'
        headers = {
            'Range': 'tournaments=0-49'
        }
        r = self.send_request(url, headers, settings.REQUEST_METHOD['get'])
        tournaments = [Tournament(**x) for x in r.json()]
        return tournaments

    def get_participants(self, tournament_id):
        """参加者データ取得

        Args:
            tournament_id (int): トーナメントID

        Returns:
            List[Participant]: 参加者データ
        """

        url = f'/tournaments/{tournament_id}/participants'
        headers = {
            'Range': 'participants=0-49'
        }
        r = self.send_request(url, headers, settings.REQUEST_METHOD['get'])
        participants = [Participant(**x) for x in r.json()]
        return participants

    def get_groups(self, tournament_id):
        """グループデータ取得

        Args:
            tournament_id (int): トーナメントID

        Returns:
            List[Group]: グループデータ
        """

        url = f'/tournaments/{tournament_id}/groups'
        headers = {
            'Range': 'groups=0-49'
        }
        r = self.send_request(url, headers, settings.REQUEST_METHOD['get'])
        groups = [Group(**x) for x in r.json()]
        return groups

    def get_stages(self, tournament_id):
        """ステージデータ取得

        Args:
            tournament_id (int): トーナメントID

        Returns:
            List[Stage]: ステージデータ
        """

        url = f'/tournaments/{tournament_id}/stages'
        r = self.send_request(url)
        stages = [Stage(**x) for x in r.json()]
        return stages

    def get_matches(self, tournament_id):
        """マッチデータ取得

        Args:
            tournament_id (int): トーナメントID

        Returns:
            List[Match]: マッチデータ
        """

        url = f'/tournaments/{tournament_id}/matches'
        headers = {
            'Range': 'matches=0-99'
        }
        r = self.send_request(url, headers=headers)
        ret = r.json()
        matches = [Match(**x) for x in r.json()]
        return matches

    def get_match_games(self, tournament_id, match_id):
        """マッチ内の各試合データ取得

        Args:
            tournament_id (int): トーナメントID
            match_id (int): マッチID

        Returns:
            List[MatchGame]: マッチ内の各試合データ
        """

        url = f'/tournaments/{tournament_id}/matches/{match_id}/games'
        headers = {
            'Range': 'games=0-49'
        }
        r = self.send_request(url, headers=headers)
        ret = r.json()
        match_games = [MatchGame(**x) for x in r.json()]
        return match_games

    def init_db(self, tournament_id, background_task_id):
        """DB初期化

        Args:
            tournament_id (int): トーナメントID
        """

        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                # Background Task Status
                values = (background_task_id, 'toornament init_db started', datetime.datetime.now())
                cursor.execute("INSERT INTO background_tasks (id, status, created_at) VALUES (%s, %s, %s)", values)

        st = None
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    tables = [
                        'teams',
                        'matches',
                        'match_opponents'
                    ]
                    for table in tables:
                        cursor.execute(f'TRUNCATE TABLE {table}')

                    # チーム情報書き換え
                    participants = self.get_participants(tournament_id)
                    for participant in participants:
                        id = participant.id
                        name = participant.name
                        cursor.execute("SELECT ballchasing_id FROM cnv_teams WHERE toornament_id = %s", [id])
                        bc_team_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO teams (id, name, bc_team_id) VALUES (%s, %s, %s)", (id, name, bc_team_id))

                    # マッチ情報書き換え
                    match_values = {
                        'base': [],
                        'opponent': []
                    }
                    matches = self.get_matches(tournament_id)
                    for match in matches:
                        self.init_db_match(cursor, match, match_values)
                        for op in match.opponents:
                            self.init_db_match_opponent(cursor, match, op, match_values)

                    # Bulk Insert
                    self.bulk_insert_match(cursor, match_values)

                except:
                    st = traceback.format_exc()

        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                # Background Task Status
                status = 'toornament init_db ended' if st is None else f'toornament init_db error: {st}'
                values = (background_task_id, status, datetime.datetime.now())
                cursor.execute("INSERT INTO background_tasks (id, status, created_at) VALUES (%s, %s, %s)", values)

    def init_db_match(self, cursor, match, match_values):
        """マッチ情報初期化

        Args:
            cursor (obj): cursor
            match (Match): マッチ情報
            match_values (array): 登録データ
        """
        values = (
            match.id,
            match.status,
            match.stage_id,
            match.group_id,
            match.round_id,
            match.number,
            match.type,
            match.scheduled_datetime,
            match.public_note,
            match.private_note,
            match.played_at,
            match.report_closed
        )

        match_values['base'].append(values)

    def init_db_match_opponent(self, cursor, match, op, match_values):
        """マッチ詳細情報初期化

        Args:
            cursor (obj): cursor
            match (Match): マッチ情報
            op (Opponent): マッチ詳細情報
            match_values (array): 登録データ
        """
        values = (
            match.id,
            op.number,
            op.position,
            op.result,
            op.rank,
            op.forfeit,
            op.score,
            op.participant.id
        )

        match_values['opponent'].append(values)

    def bulk_insert_match(self, cursor, values):
        """マッチ情報 BULK INSERT

        Args:
            cursor ([type]): [description]
            values ([type]): [description]
        """
        extras.execute_values(
            cursor, "INSERT INTO matches (id, status, stage_id, group_id, round_id, number, type, scheduled_datetime, public_note, private_note, played_at, report_closed) VALUES %s", values['base'])
        extras.execute_values(
            cursor, "INSERT INTO match_opponents (match_id, number, position, result, rank, forfeit, score, participant_id) VALUES %s", values['opponent'])
