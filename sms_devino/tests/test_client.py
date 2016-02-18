# coding: utf-8
import datetime
import time
from unittest import TestCase
from unittest.mock import patch

from .. import client


class SmsStateTestCase(TestCase):
    def test_parse_state(self):
        state_data = {
            'State': 0,
            'StateDescription': 'Доставлено',
            'Price': 1.5,
            'SubmittedDateUtc': '/Date(1455820738000)/',
            'TimeStampUtc': '/Date(1455820744000)/',
            'CreationDateUtc': '/Date(1455820738000)/',
            'ReportedDateUtc': '/Date(1455820744000)/'
        }
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


class DevinoClientTestCase(TestCase):
    def setUp(self):
        self.client = client.DevinoClient(login='test', password='123')

    @patch.object(client, 'requests')
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

    @patch.object(client, 'requests')
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

    @patch.object(client, 'requests')
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

    # def test_get_session_id(self):


    # def test_get_balance(self):
    #