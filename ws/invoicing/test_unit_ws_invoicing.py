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

    def assertTransactionEquals(self, transaction, user, amount, currency, transaction_type, date_time=None):
        self.assertEquals(transaction['user'], user)
        self.assertEquals(transaction['amount'], amount)
        #TODO transform amount to numbers.
        self.assertEquals(transaction['currency'], currency)
        self.assertEquals(transaction['transaction_type'], transaction_type)
        if date_time is not None:
            self.assertEquals(transaction['date_time'], date_time)

    def test_invoice_list_post_loading_credit_card(self):
        """
        POST a transaction and checks the answer.
        """
        # POST
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }
        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertJsonContentType(rv_post)
        self.assertEquals(rv_post.status_code, 201)
        resp = json.loads(rv_post.data)
        self.assertTransactionEquals(resp, ref_transaction['user'],
                                     ref_transaction['amount'],
                                     ref_transaction['currency'],
                                     ref_transaction['transaction_type'])
