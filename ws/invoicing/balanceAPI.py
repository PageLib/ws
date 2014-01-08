#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, marshal
from sqlalchemy.sql import func, exists
from model import Printing, LoadingCreditCard, HelpDesk, Transaction
from fields import printing_fields, loading_credit_card_fields, help_desk_fields
from app import db


class BalanceAPI(Resource):
    def __init__(self):
        super(BalanceAPI, self).__init__()

    def get(self, user_id):
        """
        GET the balance of a given user.
        """
        #TODO check if the User ID exists in the user DB.

        balance = db.session.query(func.sum(Transaction.amount).label('sum'))\
                    .filter(Transaction.user == user_id).scalar()

        return {
            'user_id': user_id,
            'balance': balance if balance is not None else 0
        }
