# -*- coding: utf-8 -*-
from flask_restful import Resource
from flask import request
from sqlalchemy.sql import func
from model import Transaction
from ws.common.helpers import ensure_allowed


class BalanceAPI(Resource):
    def __init__(self):
        super(BalanceAPI, self).__init__()

    def get(self, user_id):
        """
        GET the balance of a given user.
        """
        resource = 'own_transaction' if user_id == request.ws_session.user_id else 'transaction'
        ensure_allowed('read', resource)

        balance = request.dbs.query(func.sum(Transaction.amount).label('sum'))\
            .filter(Transaction.user_id == user_id).scalar()

        return {
            'user_id': user_id,
            'balance': balance if balance is not None else 0
        }
