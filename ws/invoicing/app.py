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
from TransactionAPI import TransactionAPI
from BalanceAPI import BalanceAPI

@app.errorhandler(412)
def not_found(error):
    return make_response(jsonify({'error': error}), 412)

api = Api(app)

api.add_resource(TransactionListAPI, '/v1/transactions', endpoint='transactions')
api.add_resource(TransactionAPI, '/v1/transactions/<string:id>', endpoint='transaction')
api.add_resource(BalanceAPI, '/v1/user/<string:user_id>/balance', endpoint='balance')
