#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse, marshal
from model import Printing, LoadingCreditCard, HelpDesk, Transaction
from fields import printing_fields, loading_credit_card_fields, help_desk_fields
from app import db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class InvoicingAPI(Resource):

    def __init__(self):
        super(InvoicingAPI, self).__init__()

    def get(self, id):
        """
        GET a transaction with a given id.
        """
        try:
            # Find the transaction.
            t = db.session.query(Transaction).filter_by(id=id).one()
            return marshal(t.to_dict(), t.get_fields)

        except NoResultFound:
            return '', 404

        except MultipleResultsFound:
            # TODO: log something
            return '', 500


