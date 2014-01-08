# -*- coding: utf-8 -*-
import os
from flask import Flask, make_response, jsonify, request
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
config_path = os.environ.get('PAGELIB_WS_INVOICING_CONFIG',
                             os.path.dirname(__file__) + '/config.py')
app.config.from_pyfile(config_path)

db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
DBSession = sessionmaker(db_engine)


@app.before_request
def open_session():
    setattr(request, 'dbs', DBSession())


@app.after_request
def commit_session(response):
    request.dbs.commit()
    return response


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
