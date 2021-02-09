import requests
from apps import settings


class Ballchasing:

    BASE_URL = 'https://ballchasing.com/api'

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
            'Authorization': settings.BCS_API_KEY
        }
        req_headers = {**base_headers, **headers}

        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=req_headers)

    def get_group(self, group_id):
        """グループデータ取得

        Args:
            group_id (int): グループID

        Returns:
            List[Group]: グループデータ
        """

        url = f'/groups/{group_id}'
        r = self.send_request(url)
        group = r.json()
        return group
