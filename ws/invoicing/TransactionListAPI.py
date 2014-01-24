# -*- coding: utf-8 -*-
from datetime import datetime
from flask_restful import Resource, reqparse, marshal
from flask import abort, request
from model import Printing, LoadingCreditCard, HelpDesk, Transaction
from ws.common.helpers import generate_uuid_for, get_or_412


class TransactionListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('amount', type=float, location='json')
        self.reqparse.add_argument('transaction_type', type=str, location='json')
        self.reqparse.add_argument('currency', type=str, location='json')
        self.reqparse.add_argument('user_id', type=str, location=('json', 'values'))
        self.reqparse.add_argument('copies', type=int, location='json')
        self.reqparse.add_argument('pages_color', type=int, location='json')
        self.reqparse.add_argument('pages_grey_level', type=int, location='json')
        self.reqparse.add_argument('from', type=str, location='values')
        self.reqparse.add_argument('to', type=str, location='values')
        super(TransactionListAPI, self).__init__()

    def get(self):
        query = request.dbs.query(Transaction)

        # Optional filters
        args = self.reqparse.parse_args()
        if args.get('user_id', None):
            query = query.filter(Transaction.user_id == args['user_id'])

        if args.get('from', None):
            try:
                date_from = datetime.strptime(args['from'], '%Y-%m-%d')
                query = query.filter(Transaction.date_time >= date_from)
            except ValueError:
                abort(412)

        if args.get('to', None):
            try:
                date_to = datetime.strptime(args['to'], '%Y-%m-%d')
                query = query.filter(Transaction.date_time <= date_to)
            except ValueError:
                abort(412)

        return {'transactions': map(lambda t: marshal(t.to_dict(), t.get_fields()), query.all())}

    def post(self):
        """
        Create a new transaction.
        """
        args = self.reqparse.parse_args()

        # Check if the required fields are present.
        transaction_type = get_or_412(args, 'transaction_type')
        amount = get_or_412(args, 'amount')
        currency = get_or_412(args, 'currency')
        user_id = get_or_412(args, 'user_id')

        if len(user_id) != 32:
            return {'error': 'The user id has not the good length.'}, 412
        if len(currency) != 3:
            return {'error': 'The currency has not the good length.'}, 412
        #TODO check if the user exists.

        if transaction_type == 'printing':
            pages_color = args.get('pages_color', 0)
            pages_grey_level = args.get('pages_grey_level', 0)

            # Check if the printing has pages (grey or color).
            if pages_color == 0 and pages_grey_level == 0:
                return {'error': 'No color or grey level page.'}, 412

            copies = get_or_412(args, 'copies')

            # Check if the printing has a positive number of copies.
            if copies <= 0:
                return {'error': 'Null number of copies.'}, 412

            if amount >= 0:
                return {'error': 'Positive amount (should be negative for a printing).'}, 412

            #TODO check the user balance.
            #TODO check the coherence between the amount and others variables.
            t = Printing(generate_uuid_for(request.dbs, Transaction), user_id, amount, currency, pages_color, pages_grey_level, copies)


        elif transaction_type == 'loading_credit_card':
            if amount <= 0:
                return {'error': 'Negative amount (should be positive for a printing).'}, 412

            t = LoadingCreditCard(generate_uuid_for(request.dbs, Transaction), user_id, amount, currency)

        elif transaction_type == 'help_desk':
            id = generate_uuid_for(request.dbs, Transaction)
            t = HelpDesk(id, user_id, amount, currency)

        # If the type is not good
        else:
            return {'error': 'Unknown type.'}, 412

        request.dbs.add(t)

        return marshal(t.to_dict(), t.get_fields()), 201
