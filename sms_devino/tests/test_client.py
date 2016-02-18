# coding: utf-8
import datetime
import time
from unittest import TestCase
from .. import client


class SmsState(TestCase):

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
