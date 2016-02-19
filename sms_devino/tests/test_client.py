# coding: utf-8
import datetime
import time
from unittest import TestCase
from unittest.mock import patch

from .. import client


def get_state_data():
    return {
        'State': 0,
        'StateDescription': 'Доставлено',
        'Price': 1.5,
        'SubmittedDateUtc': '/Date(1455820738000)/',
        'TimeStampUtc': '/Date(1455820744000)/',
        'CreationDateUtc': '/Date(1455820738000)/',
        'ReportedDateUtc': '/Date(1455820744000)/'
    }


class SmsStateTestCase(TestCase):
    def test_parse_state(self):
        state_data = get_state_data()
        state = client.SmsState.parse_state(state_data)
        self.assertEqual(state.code, state_data['State'])
        self.assertEqual(state.description, state_data['StateDescription'])
        self.assertEqual(state.submitted_dt, client.SmsState._parse_date(state_data['SubmittedDateUtc']))
        self.assertEqual(state.result_dt, client.SmsState._parse_date(state_data['TimeStampUtc']))
        self.assertEqual(state.creation_dt, client.SmsState._parse_date(state_data['CreationDateUtc']))
        self.assertEqual(state.reported_dt, client.SmsState._parse_date(state_data['ReportedDateUtc']))

    def test_parse_date(self):
        now = datetime.datetime.now().replace(microsecond=0)
        timestamp_sec = int(time.mktime(now.timetuple()))
        timestamp_milli_sec = timestamp_sec * 1000
        date_str = '/Date({0})/'.format(timestamp_milli_sec)

        parsed_dt = client.SmsState._parse_date(date_str)
        self.assertEqual(parsed_dt, now)


@patch.object(client, 'requests')
class DevinoClientTestCase(TestCase):
    def setUp(self):
        self.client = client.DevinoClient(login='test', password='123')

    def test_request_get(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.get.called)

        result = self.client._request('/some_url/', {'test': 123})

        self.assertTrue(requests_mock.get.called)
        self.assertEqual(
            result,
            requests_mock.get.return_value.json.return_value,
        )

    def test_request_post(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.post.called)

        result = self.client._request('/some_url/', {'test': 123}, method=client.METHOD_POST)

        self.assertTrue(requests_mock.post.called)
        self.assertEqual(
            result,
            requests_mock.post.return_value.json.return_value,
        )

    def test_request_status_error(self, requests_mock):
        error_data = {'Code': 123, 'Desc': 'test error'}
        requests_mock.get.return_value.status_code = 400
        requests_mock.get.return_value.json.return_value = error_data
        self.assertFalse(requests_mock.get.called)

        exception = None
        try:
            self.client._request('/some_url/', {'test': 123}, method=client.METHOD_GET)
        except client.DevinoException as ex:
            exception = ex

        self.assertTrue(requests_mock.get.called)
        self.assertIsNotNone(exception)
        self.assertEqual(exception.http_status, requests_mock.get.return_value.status_code)
        self.assertEqual(exception.error.code, error_data['Code'])
        self.assertEqual(exception.error.description, error_data['Desc'])

    def test_get_session_id(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = 'session_id_123'
        self.assertEqual(requests_mock.get.call_count, 0)

        session_id = self.client._get_session_id()
        self.assertEqual(session_id, requests_mock.get.return_value.json.return_value)
        self.assertEqual(requests_mock.get.call_count, 1)

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.SESSION_URL, call_args[0])
        self.assertEqual(self.client.login, call_kwargs['params']['login'])
        self.assertEqual(self.client.password, call_kwargs['params']['password'])

        # no additional calls
        self.client._get_session_id()
        self.assertEqual(requests_mock.get.call_count, 1)

    def test_get_balance(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = 100500

        balance = self.client.get_balance()
        self.assertEqual(balance, requests_mock.get.return_value.json.return_value)

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.BALANCE_URL, call_args[0])

    def test_send_one(self, requests_mock):
        self.client._session_id = '123321'
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = ['1', '2']

        source_address = 'MyOrg'
        destination_address = '89151234567'
        message = 'Hello!'
        result = self.client.send_one(source_address, destination_address, message)
        self.assertEqual(result.address, destination_address)
        self.assertEqual(result.sms_ids, requests_mock.post.return_value.json.return_value)

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.SEND_ONE_URL, call_args[0])
        self.assertEqual(self.client._session_id, call_kwargs['data']['sessionId'])
        self.assertEqual(source_address, call_kwargs['data']['sourceAddress'])
        self.assertEqual(destination_address, call_kwargs['data']['destinationAddress'])
        self.assertEqual(message, call_kwargs['data']['data'])
        self.assertEqual(0, call_kwargs['data']['validity'])

    def test_send_bulk(self, requests_mock):
        self.client._session_id = '123321'
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = ['1.1', '1.2', '2.1', '2.2']

        source_address = 'MyOrg'
        destination_addresses = ['89151234567', '89157654321']
        message = 'Hello!'
        results = self.client.send_bulk(source_address, destination_addresses, message)
        for i, address in enumerate(destination_addresses):
            result = results[i]
            self.assertEqual(result.address, address)
            self.assertEqual(result.sms_ids, requests_mock.post.return_value.json.return_value[i*2:i*2+2])

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.SEND_BULK_URL, call_args[0])
        self.assertEqual(self.client._session_id, call_kwargs['data']['sessionId'])
        self.assertEqual(source_address, call_kwargs['data']['sourceAddress'])
        self.assertEqual(destination_addresses, call_kwargs['data']['DestinationAddresses'])
        self.assertEqual(message, call_kwargs['data']['data'])
        self.assertEqual(0, call_kwargs['data']['validity'])

    def test_get_state(self, requests_mock):
        self.client._session_id = '123321'
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = get_state_data()

        sms_id = '123456'
        state = self.client.get_state(sms_id)
        self.assertEqual(state.code, requests_mock.get.return_value.json.return_value['State'])
