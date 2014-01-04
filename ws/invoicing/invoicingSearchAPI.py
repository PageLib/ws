#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
from model import Printing, LoadingCreditCard, HelpDesk, Transaction
from fields import printing_fields, loading_credit_card_fields, help_desk_fields
from app import db


class InvoicingSearchAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user', type=str, location='values')
        self.reqparse.add_argument('from', type=str, location='values')
        super(InvoicingSearchAPI, self).__init__()

    def get(self):
        query = db.session.query(Transaction)

        # Optional filters
        args = self.reqparse.parse_args()
        if args.get('user', None):
            query = query.filter(Transaction.user == args['user'])
        return {'transactions': map(lambda t: marshal(t.to_dict(), t.get_fields()), query.all())}