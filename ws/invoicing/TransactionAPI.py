# -*- coding: utf-8 -*-
from flask_restful import Resource, marshal
from model import Transaction
from flask import request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from ws.common.helpers import ensure_allowed


class TransactionAPI(Resource):

    def __init__(self):
        super(TransactionAPI, self).__init__()

    def get(self, id):
        """
        GET a transaction with a given id.
        """
        try:
            # Find the transaction.
            t = request.dbs.query(Transaction).filter_by(id=id).one()

            # Check permissions (issue: allow to know about the data even with credentials)
            resource = 'own_transaction' if t.user_id == request.ws_session.user_id else 'transaction'
            ensure_allowed('read', resource)

            return marshal(t.to_dict(), t.get_fields())
        except NoResultFound:
            return '', 404

        except MultipleResultsFound:
            # TODO: log something
            return '', 500

