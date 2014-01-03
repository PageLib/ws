__author__ = 'Alexis'

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

    def assertTransactionEquals(self, t1, t2):
        self.assertEquals(t1['user'], t2['user'])
        amount1 = float(t1['amount'])
        amount2 = float(t2['amount'])
        self.assertEquals(amount1, amount2)
        self.assertEquals(t1['currency'], t2['currency'])
        self.assertEquals(t1['transaction_type'], t2['transaction_type'])
        if 'date_time' in t1.keys() and 'date_time' in t2.keys():
            if t1['date_time'] is not None and t2['date_time'] is not None:
                self.assertEquals(t1['date_time'], t2['date_time'])

    def test_invoice_list_post_loading_credit_card(self):
        """
        POST a transaction, checks the answer and gets it.
        """
        # POST
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }
        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertJsonContentType(rv_post)
        self.assertEquals(rv_post.status_code, 201)
        resp_post = json.loads(rv_post.data)
        self.assertTransactionEquals(resp_post, ref_transaction)

        # GET
        uri = str(resp_post['uri'])
        print(uri)
        rv_get = self.app.get(uri)
        self.assertJsonContentType(rv_get)
        self.assertEquals(rv_get.status_code, 200)
        resp_get = json.loads(rv_get.data)
        self.assertTransactionEquals(resp_post, resp_get)

