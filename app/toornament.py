import json
import requests
import app.settings as settings

from models.tournament import Tournament
from models.participant import Participant
from models.group import Group


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
        self.access_token = self.get_access_token()

    def get_access_token(self):
        """アクセストークン取得

        Returns:
            str: アクセストークン
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
        return data['access_token']

    def send_request(self, url, headers_option, method):
        """リクエスト送信

        Args:
            url (str): URL
            headers_option (dict): Header情報
            method (string): Method

        Returns:
            Response: レスポンス
        """

        request_url = self.BASE_URL + url
        base_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Api-Key': settings.API_KEY
        }
        headers = {**base_headers, **headers_option}

        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=headers)

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
