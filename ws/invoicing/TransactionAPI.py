#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, marshal
from model import Transaction
from flask import g
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class TransactionAPI(Resource):

    def __init__(self):
        super(TransactionAPI, self).__init__()

    def get(self, id):
        """
        GET a transaction with a given id.
        """
        dbs = g.DBSession()
        try:
            # Find the transaction.
            t = dbs.query(Transaction).filter_by(id=id).one()
            return marshal(t.to_dict(), t.get_fields())

        except NoResultFound:
            return '', 404

        except MultipleResultsFound:
            # TODO: log something
            return '', 500


