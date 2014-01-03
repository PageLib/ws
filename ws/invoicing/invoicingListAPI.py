#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
from model import Printing, LoadingCreditCard, HelpDesk
from fields import printing_fields, loading_credit_card_fields, help_desk_fields
from app import db


class InvoicingListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('amount', type=int, required=True, location='json',
                                   help='No amount provided')
        self.reqparse.add_argument('transaction_type', type=str, location='json',
                                   required=True, help='No type provided')
        self.reqparse.add_argument('currency', type=str, location='json',
                                   required=True, help='No currency provided')
        self.reqparse.add_argument('user', type=str, location='json',
                                   required=True, help='No user provided')
        self.reqparse.add_argument('copies', type=int, location='json')
        self.reqparse.add_argument('pages_color', type=int, location='json')
        self.reqparse.add_argument('pages_grey_level', type=int, location='json')
        super(InvoicingListAPI, self).__init__()

    def post(self):
        """
        Create a new transaction.
        """
        args = self.reqparse.parse_args()
        transaction_type = args['transaction_type']
        amount = args['amount']
        currency = args['currency']
        user = args['user']

        if transaction_type == 'printing':
            pages_color = args['pages_color']
            copies = args['copies']
            pages_grey_level = args['pages_grey_level']
            #TODO gerer les nulls dans les pages et copies.
            t = Printing(user, amount, currency, pages_color, pages_grey_level, copies)

        elif transaction_type == 'loading_credit_card':
            t = LoadingCreditCard(user, amount, currency)

        elif transaction_type == 'help_desk':
            t = HelpDesk(user, amount, currency)

        #If the type is not good
        else:
            return {'error': 'Type unknown'}, 412

        db.session.add(t)
        db.session.commit()
        return marshal(t.to_dict(), t.get_fields()), 201


