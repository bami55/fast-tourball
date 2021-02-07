import json
import requests
import app.settings as settings

from models.tournament import Tournament
from models.participant import Participant

class Toornament:

    BASE_URL = 'https://api.toornament.com/organizer/v2'

    access_token = None

    def __init__(self, *args, **kwargs):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        url = 'https://api.toornament.com/oauth/v2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'scope': 'organizer:view organizer:admin organizer:participant',
        }
        r = requests.post(url, data=data)
        data = r.json()
        return data['access_token']

    def send_request(self, url, headers_option, method):
        request_url = self.BASE_URL + url
        base_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Api-Key': settings.API_KEY
        }
        headers = {**base_headers, **headers_option}
        
        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=headers)

    def get_tournaments(self):
        url = '/tournaments'
        headers = {
            'Range': 'tournaments=0-49'
        }
        r = self.send_request(url, headers, settings.REQUEST_METHOD['get'])
        tournaments = r.json()
        
        ret = Tournament(**t) for t in tournaments
        return ret

    def get_participants(self, tournament_id):
        url = f'/tournaments/{tournament_id}/participants'
        headers = {
            'Range': 'participants=0-49'
        }
        r = self.send_request(url, headers, settings.REQUEST_METHOD['get'])
        participants = r.json()
        
        ret = Participant(**p) for p in participants
        return ret
