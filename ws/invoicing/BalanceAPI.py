#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource
from flask import request
from sqlalchemy.sql import func
from model import Transaction



class BalanceAPI(Resource):
    def __init__(self):
        super(BalanceAPI, self).__init__()

    def get(self, user_id):
        """
        GET the balance of a given user.
        """
        #TODO check if the User ID exists in the user DB.

        balance = request.dbs.query(func.sum(Transaction.amount).label('sum'))\
            .filter(Transaction.user_id == user_id).scalar()

        return {
            'user_id': user_id,
            'balance': balance if balance is not None else 0
        }
