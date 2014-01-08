# -*- coding: utf-8 -*-
import os
from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

config_obj = os.environ.get("PAGELIB_WS_INVOICING_CONFIG", "config_dev")

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(config_obj)

from TransactionListAPI import TransactionListAPI
from invoicingAPI import InvoicingAPI
from balanceAPI import BalanceAPI

@app.errorhandler(412)
def not_found(error):
    return make_response(jsonify({'error': error}), 412)

api = Api(app)

api.add_resource(TransactionListAPI, '/v1/invoices', endpoint='invoices')
api.add_resource(InvoicingAPI, '/v1/invoices/<string:id>', endpoint='invoice')
api.add_resource(BalanceAPI, '/v1/user/balance/<string:id>', endpoint='balance')
