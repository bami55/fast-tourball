import json
import requests
from api import settings

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

    def __init__(self, *args, **kwargs):
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
