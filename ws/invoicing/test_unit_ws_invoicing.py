# -*- coding: utf-8 -*-

import os
os.environ['DIAG_CONFIG_MODULE'] = 'config_test'
import json
from app import db
import app
import unittest
import copy

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

        # Verification specific to the printing class
        if t1['transaction_type'] == 'printing':
            # A printing may not have page_color or page_grey_level.
            if 'pages_color' in t1.keys() and 'pages_color' in t2.keys():
                self.assertEquals(t1['pages_color'], t2['pages_color'])
            if 'pages_grey_level' in t1.keys() and 'pages_grey_level' in t2.keys():
                self.assertEquals(t1['pages_grey_level'], t2['pages_grey_level'])
            self.assertEquals(t1['copies'], t2['copies'])
            print(t1)
            print(t2)

    def test_invoice_list_post_ok(self):
        """
        POST transactions, checks the answer and gets it.
        The transactions are
        * loading_credit_card
        * 3 printings with
            * both color and grey
            * only grey
            * only color
        * help desk
        """
        # POST
        ref_transaction_loading_credit_card = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        ref_transaction_printing_both = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 3.0,
            'currency': 'EUR',
            'transaction_type': 'printing',
            'pages_color': 2,
            'pages_grey_level': 3,
            'copies': 3
        }

        ref_transaction_printing_grey = copy.copy(ref_transaction_printing_both)
        ref_transaction_printing_grey.pop('pages_color')

        ref_transaction_printing_color = copy.copy(ref_transaction_printing_both)
        ref_transaction_printing_color.pop('pages_grey_level')
        # Le comportement du logiciel est bizarre: il met 0 dans le champs si on lui
        # donne rien. Je sais psa si ca pose problème.
        ref_transaction_help_desk = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'help_desk'
        }
        transactions = [ref_transaction_loading_credit_card, ref_transaction_printing_both,
                        ref_transaction_printing_grey, ref_transaction_printing_color,
                        ref_transaction_help_desk]
        for ref_transaction in transactions:
            rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                    content_type='application/json')
            self.assertJsonContentType(rv_post)
            self.assertEquals(rv_post.status_code, 201)
            resp_post = json.loads(rv_post.data)
            self.assertTransactionEquals(resp_post, ref_transaction)

            # GET
            # uri = str(resp_post['uri'])
            # print(uri)
            # rv_get = self.app.get(uri)
            # self.assertJsonContentType(rv_get)
            # self.assertEquals(rv_get.status_code, 200)
            # resp_get = json.loads(rv_get.data)
            # self.assertTransactionEquals(resp_post, resp_get)

    def test_invoice_list_post_bad_user(self):
        """
        POST a transaction with a bad user
        (not the good number of characters in the uuid).
        """
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA9509DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertEquals(rv_post.status_code, 412)

    def test_invoice_list_bad_amount(self):
        """
        POST a transaction with a bad amount and expects an error.
        """
        # POST
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 'a',
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertEquals(rv_post.status_code, 400)

    def test_invoice_list_no_user(self):
        """
        POST a transaction with no user.
        """

        ref_transaction = {
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertEquals(rv_post.status_code, 400)

    def test_invoice_list_no_amount(self):
        """
        POST a transaction with no amount
        """
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertJsonContentType(rv_post)
        self.assertEquals(rv_post.status_code, 400)

    def test_invoice_list_bad_transaction_type(self):
        """
        POST a transaction with a bad transaction_type.
        """
        ref_transaction = {
            'user': 'D6F1FF4199954F0EA956DB4709DC227A',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'plop'
        }

        rv_post = self.app.post('/v1/invoices', data=json.dumps(ref_transaction),
                                content_type='application/json')
        self.assertJsonContentType(rv_post)
        self.assertEquals(rv_post.status_code, 412)