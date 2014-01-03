# -*- coding: utf-8 -*-

import os
os.environ['DIAG_CONFIG_MODULE'] = 'config_test'
import json
from app import db
import app
import unittest

class InvoiceTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assertJsonContentType(self, rv):
        self.assertEquals(rv.headers['Content-type'], 'application/json')

    def test_balance_ok(self):
        """
        POST transactions and checks the balance.
        """
        loading_t = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        loading_t_other_user = {
            'user': 'D6F1FF419ANOTHERAUSERB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        printing1_t = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': -3.0,
            'currency': 'EUR',
            'transaction_type': 'printing',
            'pages_color': 2,
            'pages_grey_level': 3,
            'copies': 3
        }

        help_desk_t = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'help_desk'
        }
        for t in [loading_t, loading_t_other_user, printing1_t, help_desk_t]:
            self.app.post('/v1/invoices', data=json.dumps(t), content_type='application/json')
        rv = self.app.get('/v1/user/balance/D6F1FF4199954F0EA956DB4709DC227A')
        self.assertJsonContentType(rv)
        self.assertEquals(rv.status_code, 200)
        resp = json.loads(rv.data)
        self.assertEquals('D6F1FF4199954F0EA956DB4709DC227A', resp['user_id'])
        self.assertEquals(7.00, resp['balance'])


