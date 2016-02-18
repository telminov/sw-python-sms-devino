# coding: utf-8
import requests


REST_URL = 'https://integrationapi.net/rest'
SESSION_URL = '/user/sessionId'
BALANCE_URL = '/user/balance'
SEND_ONE_URL = '/sms/send'
SEND_BULK_URL = '/sms/sendBulk'
STATE_URL = '/sms/state'

METHOD_GET = 'get'
METHOD_POST = 'post'


class DevinoException(Exception):
    def __init__(self, message: str, http_status: int, description: str = None, code: int = None,
                 base_exception: Exception = None):
        self.message = message
        self.http_status = http_status
        self.description = description
        self.code = code
        self.base_exception = base_exception


class DevinoClient:

    def __init__(self, login: str, password: str, url: str =REST_URL):
        self.login = login
        self.password = password
        self.url = url
        self._session_id = None

    def get_balance(self) -> float:
        session_id = self._get_session_id()
        return self._request(BALANCE_URL, {'sessionId': session_id})

    def _get_session_id(self) -> str:
        if not self._session_id:
            self._session_id = self._request(SESSION_URL, {'login': self.login, 'password': self.password})
        return self._session_id

    def _request(self, path, params=None, method=METHOD_GET):
        request_url = self.url + path

        if method == METHOD_GET:
            response = requests.get(request_url, params=params)
        else:
            response = requests.post(request_url, data=params)

        if 400 <= response.status_code <= 500:
            error_description = response.json()
            raise DevinoException(
                message='Ошибка отправки',
                http_status=response.status_code,
                description=error_description.get('Desc'),
                code=error_description.get('Code'),
            )

        return response.json()



if __name__ == '__main__':
    # quick test: python client.py tester 123
    import sys
    login = sys.argv[1]
    passwd = sys.argv[2]
    client = DevinoClient(login, passwd)
    print(client.get_balance())
