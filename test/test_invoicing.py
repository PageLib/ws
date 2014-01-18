# -*- coding: utf-8 -*-

import datetime
import json
from WsTestCase import WsTestCase
from copy import copy
import requests


class InvoiceTestCase(WsTestCase):

    ref_transaction_loading_credit_card = {
        'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
        'amount': 5.0,
        'currency': 'EUR',
        'transaction_type': 'loading_credit_card'
    }

    ref_transaction_printing_both = {
        'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
        'amount': -3.0,
        'currency': 'EUR',
        'transaction_type': 'printing',
        'pages_color': 2,
        'pages_grey_level': 3,
        'copies': 3
    }
    ref_transaction_help_desk = {
        'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
        'amount': 5.0,
        'currency': 'EUR',
        'transaction_type': 'help_desk'
    }

    def assertJsonContentType(self, rv):
        self.assertEquals('application/json', rv.headers['Content-type'], rv)

    def assertTransactionEquals(self, t1, t2):
        """
        Check if t1 and t2 are equal.
        If one has no date_time, date_time is not checked.
        It's the same for pages_color, pages_grey_level if it's a printing instance.
        """
        self.assertEquals(t1['user_id'], t2['user_id'])
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
        #Create test data.
        ref_transaction_printing_grey = copy(self.ref_transaction_printing_both)
        ref_transaction_printing_grey.pop('pages_color')

        ref_transaction_printing_color = copy(self.ref_transaction_printing_both)
        ref_transaction_printing_color.pop('pages_grey_level')
        # Le comportement du logiciel est bizarre: il met 0 dans le champs si on lui
        # donne rien. Je sais psa si ca pose problème.
        transactions = [self.ref_transaction_loading_credit_card, self.ref_transaction_printing_both,
                        ref_transaction_printing_grey, ref_transaction_printing_color,
                        self.ref_transaction_help_desk]

        for ref_transaction in transactions:
            # POST
            rv_post = requests.post(self.invoicing_endpoint + '/v1/transactions',
                                    data=json.dumps(ref_transaction),
                                    headers={'Content-type': 'application/json'})
            self.assertJsonContentType(rv_post)
            self.assertEquals(rv_post.status_code, 201, ref_transaction)
            resp_post = rv_post.json()
            self.assertTransactionEquals(resp_post, ref_transaction)

            # GET
            rv_get = requests.get(self.invoicing_endpoint + '/v1/transactions/' + resp_post['id'])
            self.assertJsonContentType(rv_get)
            self.assertEquals(rv_get.status_code, 200)
            resp_get = rv_get.json()
            self.assertTransactionEquals(resp_post, resp_get)

    def test_invoice_list_search(self):
        """
        POST 4 transactions in the DB and search the ones from a given user.
        We check the number of transactions answered and that they belong
        to the good person.
        """
        ref_transaction_loading_credit_card_other_user = copy(self.ref_transaction_loading_credit_card)
        ref_transaction_loading_credit_card_other_user['user_id'] = 'd6f1ff419anotheruserdb4709dc227a'

        transactions = [self.ref_transaction_loading_credit_card,
                        self.ref_transaction_printing_both,
                        self.ref_transaction_help_desk,
                        ref_transaction_loading_credit_card_other_user]

        for t in transactions:
            requests.post(self.invoicing_endpoint + '/v1/transactions',
                          data=json.dumps(t), headers={'Content-type': 'application/json'})

        rv = requests.get(self.invoicing_endpoint + '/v1/transactions?user_id=d6f1ff4199954f0ea956db4709dc227a')
        resp = rv.json()
        self.assertEquals(len(resp['transactions']), 3)
        for t in resp['transactions']:
            self.assertEquals(t['user_id'], 'd6f1ff4199954f0ea956db4709dc227a')

        #We check the transactions issued from today.
        # Le problème c'est que les données sont pas bones pour le test.
        # On ne peut fair qu'un test qui soit les prend tous ou aucun.
        date_from_1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        rv_1 = requests.get(self.invoicing_endpoint + '/v1/transactions?from=' + date_from_1)
        resp_1 = rv_1.json()
        self.assertEquals(len(resp_1['transactions']), 4)

        # We check the transactions issued from tomorrow.
        date_from_2 = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        rv_2 = requests.get(self.invoicing_endpoint + '/v1/transactions?from=' + date_from_2)
        resp_2 = rv_2.json()
        self.assertEquals(len(resp_2['transactions']), 0)

    def test_invoice_list_error_412(self):
        """
        POST transactions which are not correct. (412 status).
        * bad user (not the good number of characters in the uuid).
        * non existing transaction type
        * 3 printing with no copies
        * no user
        * no amount
        * non integer amount
        """
        transaction_bad_user = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc2',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        transaction_bad_type = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'plop'
        }

        printing_no_copies = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
            'amount': -3.0,
            'currency': 'EUR',
            'transaction_type': 'printing',
            'pages_color': 2,
            'pages_grey_level': 3,
            'copies': 0
        }
        printing_no_pages1 = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
            'amount': -3.0,
            'currency': 'EUR',
            'transaction_type': 'printing',
            'pages_color': 0,
            'pages_grey_level': 0,
            'copies': 0
        }

        printing_no_pages2 = copy(printing_no_pages1)
        printing_no_pages2.pop('pages_color')

        printing_no_pages3 = copy(printing_no_pages1)
        printing_no_pages3.pop('pages_grey_level')

        transaction_no_user = {
            'amount': 5.0,
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        transaction_no_amount = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }
        transaction_bad_amount = {
            'user_id': 'd6f1ff4199954f0ea956db4709dc227a',
            'amount': 'a',
            'currency': 'EUR',
            'transaction_type': 'loading_credit_card'
        }

        transactions = [transaction_bad_user, transaction_bad_type,
                        printing_no_copies, printing_no_pages2,
                        printing_no_pages3, transaction_no_user,
                        transaction_no_amount, transaction_bad_amount]
        i = 0
        for ref_transaction in transactions:
            print(transactions[i])
            i += 1
            rv_post = requests.post(self.invoicing_endpoint + '/v1/transactions',
                                    data=json.dumps(ref_transaction),
                                    headers={'Content-type': 'application/json'})

            self.assertEquals(rv_post.status_code, 412)
            self.assertJsonContentType(rv_post)
            print(rv_post.json())

    def test_balance_ok(self):
        """
        POST transactions and checks the balance.
        """

        loading_t_other_user = copy(self.ref_transaction_loading_credit_card)
        loading_t_other_user['user_id'] = 'd6f1ff419anotheruserdb4709dc227a'

        for t in [self.ref_transaction_loading_credit_card,
                  loading_t_other_user,
                  self.ref_transaction_printing_both,
                  self.ref_transaction_help_desk]:
            requests.post(self.invoicing_endpoint + '/v1/transactions',
                          data=json.dumps(t), headers={'Content-type': 'application/json'})

        rv = requests.get(self.invoicing_endpoint + '/v1/user/d6f1ff4199954f0ea956db4709dc227a/balance')
        self.assertJsonContentType(rv)
        self.assertEquals(rv.status_code, 200)
        resp = rv.json()
        self.assertEquals('d6f1ff4199954f0ea956db4709dc227a', resp['user_id'])
        self.assertEquals(7.00, resp['balance'])
