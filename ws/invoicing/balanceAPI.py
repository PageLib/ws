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

    def get(self, id):
        """
        GET the balance of a given user.
        """
        #TODO check if the User ID exists in the user DB.
        #If there is no transaction the balance is 0.

        # if not db.session.query(exists().where(Transaction.id==id)).scalar():
        #     return {
        #         'user_id': id,
        #         'balance': 0
        #     }
        print(db.session.query(Transaction).all())
        balance = db.session.query(func.sum(Transaction.amount).label('sum'))\
                    .filter(Transaction.id == id).scalar()
        return {
                'user_id':id,
                'balance': balance
            }