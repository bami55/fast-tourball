import requests
from apps import settings
from models.ballchasing import ReplayGroup


class Ballchasing:

    BASE_URL = 'https://ballchasing.com/api'

    def send_request(self, url, headers={}, method=settings.REQUEST_METHOD['get'], params=None):
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
            'Authorization': settings.BCS_API_KEY
        }
        req_headers = {**base_headers, **headers}

        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=req_headers, params=params)

    def get_group(self, group_id):
        """グループデータ取得

        Args:
            group_id (int): グループID

        Returns:
            Group: グループデータ
        """

        url = f'/groups/{group_id}'
        r = self.send_request(url)
        replay_group = ReplayGroup(**r.json())
        return replay_group

    def get_group_children(self, group_id):
        """グループの子グループデータ取得

        Args:
            group_id (int): 親グループID

        Returns:
            List[Group]: 子グループデータ
        """

        url = f'/groups'
        params = {
            'group': group_id,
            'sort-by': 'created',
            'sort-dir': 'asc'
        }
        r = self.send_request(url, params=params)
        replay_groups = []
        for x in r.json()['list']:
            group = self.get_group(x['id'])
            replay_groups.append(group)
        return replay_groups
