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

    def test_invoice_list_post_loading_credit_card(self):
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }
        rv = self.app.post('/v1/invoices', data=json.dumps(ref_transaction), content_type='application/json')
        self.assertJsonContentType(rv)
        self.assertEquals(rv.status_code, 201)
