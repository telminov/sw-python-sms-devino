# coding: utf-8
import datetime
import re
import requests
from typing import List
from decimal import Decimal

REST_URL = 'https://integrationapi.net/rest'
SESSION_URL = '/user/sessionId'
BALANCE_URL = '/user/balance'
SEND_ONE_URL = '/sms/send'
SEND_BULK_URL = '/sms/sendBulk'
STATE_URL = '/sms/state'

METHOD_GET = 'get'
METHOD_POST = 'post'


# Error codes description on
# http://www.devinotele.com/resheniya/dokumentaciya-po-api/http_rest_protocol/Kody_oshibok_i_statusy_soobshcheny/
class DevinoError:
    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description


class DevinoException(Exception):
    def __init__(self, message: str, http_status: int = None, error: DevinoError = None,
                 base_exception: Exception = None):
        self.message = message
        self.http_status = http_status
        self.error = error
        self.base_exception = base_exception


class SendSmsResult:
    def __init__(self, address: str, sms_ids: List[str]):
        self.address = address
        self.sms_ids = sms_ids


class SmsState:
    """
    http://www.devinotele.com/resheniya/dokumentaciya-po-api/http_rest_protocol/Polucheniye_statusa_otpravlennogo_SMS-soobshcheniya/
    """
    def __init__(self, code: int, description: str, price: Decimal,
                 creation_dt: datetime.datetime, submitted_dt: datetime.datetime,
                 result_dt: datetime.datetime, reported_dt: datetime.datetime
                 ):
        self.code = code
        self.description = description
        self.price = price
        self.creation_dt = creation_dt
        self.submitted_dt = submitted_dt
        self.result_dt = result_dt
        self.reported_dt = reported_dt

    @classmethod
    def parse_state(cls, state_data: dict):
        return cls(
            code=int(state_data.get('State')),
            description=state_data.get('StateDescription'),
            price=Decimal(state_data.get('Price')),
            creation_dt=cls._parse_date(state_data.get('CreationDateUtc')),
            submitted_dt=cls._parse_date(state_data.get('SubmittedDateUtc')),
            result_dt=cls._parse_date(state_data.get('TimeStampUtc')),
            reported_dt=cls._parse_date(state_data.get('ReportedDateUtc')),
        )

    @staticmethod
    def _parse_date(value: str) -> datetime.datetime:
        milliseconds = int(re.search(r'\d+', value).group())
        seconds = int(milliseconds/1000)
        dt = datetime.datetime.fromtimestamp(seconds)
        return dt


class DevinoClient:

    def __init__(self, login: str, password: str, url: str = REST_URL):
        self.login = login
        self.password = password
        self.url = url
        self._session_id = None

    def get_balance(self) -> float:
        session_id = self._get_session_id()
        return self._request(BALANCE_URL, {'sessionId': session_id})

    def send_one(self, source_address: str, destination_address: str, message: str,
                 validity_minutes: int = 0) -> SendSmsResult:
        """
        http://www.devinotele.com/resheniya/dokumentaciya-po-api/http_rest_protocol/Otpravka_SMS-soobshcheny/
        """
        session_id = self._get_session_id()
        params = {
            'sessionId': session_id,
            'sourceAddress': source_address,
            'destinationAddress': destination_address,
            'data': message,
            'validity': validity_minutes,
        }
        sms_ids = self._request(SEND_ONE_URL, params, method=METHOD_POST)
        return SendSmsResult(destination_address, sms_ids)

    def send_bulk(self, source_address: str, destination_addresses: List[str], message: str,
                 validity_minutes: int = 0) -> List[SendSmsResult]:
        """
        http://www.devinotele.com/resheniya/dokumentaciya-po-api/http_rest_protocol/Otpravka_SMS-soobshcheny/
        """
        session_id = self._get_session_id()
        params = {
            'sessionId': session_id,
            'sourceAddress': source_address,
            'DestinationAddresses': destination_addresses,
            'data': message,
            'validity': validity_minutes,
        }
        all_sms_ids = self._request(SEND_BULK_URL, params, method=METHOD_POST)

        ids_per_sms = len(all_sms_ids) / len(destination_addresses)
        results = []
        message_ids = []
        for sms_id in all_sms_ids:
            message_ids.append(sms_id)

            if len(message_ids) == ids_per_sms:
                address = destination_addresses[len(results)]
                send_result = SendSmsResult(address, message_ids)
                message_ids = []
                results.append(send_result)

        return results

    def get_state(self, sms_id: str) -> SmsState:
        session_id = self._get_session_id()
        params = {'sessionId': session_id , 'messageId': sms_id}
        state_data = self._request(STATE_URL, params)
        state = SmsState.parse_state(state_data)
        return state

    def _get_session_id(self) -> str:
        if not self._session_id:
            self._session_id = self._request(SESSION_URL, {'login': self.login, 'password': self.password})
        return self._session_id

    def _request(self, path, params=None, method=METHOD_GET):
        request_url = self.url + path

        try:
            if method == METHOD_GET:
                response = requests.get(request_url, params=params)
            else:
                response = requests.post(request_url, data=params)
        except requests.ConnectionError as ex:
            raise DevinoException(
                message='Ошибка отправки',
                base_exception=ex,
            )

        if 400 <= response.status_code <= 500:
            error_description = response.json()
            error = DevinoError(
                code=error_description.get('Code'),
                description=error_description.get('Desc'),
            )
            raise DevinoException(
                message='Ошибка отправки',
                http_status=response.status_code,
                error=error,
            )

        return response.json()



if __name__ == '__main__':
    # quick test: python client.py tester 123
    import sys
    login = sys.argv[1]
    passwd = sys.argv[2]
    client = DevinoClient(login, passwd)
    print('balance', client.get_balance())