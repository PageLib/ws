#!flask/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Resource, marshal
from model import Printing, LoadingCreditCard, HelpDesk
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






