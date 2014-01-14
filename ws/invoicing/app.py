# -*- coding: utf-8 -*-
import os
import sys
import logging
from flask import Flask, make_response, jsonify, request
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model
from TransactionListAPI import TransactionListAPI
from TransactionAPI import TransactionAPI
from BalanceAPI import BalanceAPI

app = Flask(__name__)

# Load configuration
config_path = os.environ.get('PAGELIB_WS_INVOICING_CONFIG',
                             os.path.dirname(__file__) + '/config.py')
app.config.from_pyfile(config_path)

# Set up logging
if app.config['LOG_FILE'] != '':
    log_handler = logging.FileHandler(app.config['LOG_FILE'])
else:
    log_handler = logging.StreamHandler(sys.stdout)

log_handler.setLevel(app.config['LOG_LEVEL'])
log_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
app.logger.setLevel(app.config['LOG_LEVEL'])
app.logger.addHandler(log_handler)

# Prepare database connection
db_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
DBSession = sessionmaker(db_engine)

if app.config['CREATE_SCHEMA_ON_STARTUP']:
    app.logger.info('Creating database schema')
    model.Base.metadata.create_all(db_engine)


@app.before_request
def open_session():
    setattr(request, 'dbs', DBSession())


@app.after_request
def commit_session(response):
    request.dbs.commit()
    return response


@app.errorhandler(412)
def not_found(error):
    return make_response(jsonify({'error': error}), 412)

# Set up RESTful API resources
api = Api(app)
api.add_resource(TransactionListAPI, '/v1/transactions', endpoint='transactions')
api.add_resource(TransactionAPI, '/v1/transactions/<string:id>', endpoint='transaction')
api.add_resource(BalanceAPI, '/v1/user/<string:user_id>/balance', endpoint='balance')

if __name__ == '__main__':
    app.logger.info('Starting service')
    app.run(host=app.config['HOST'], port=app.config['PORT'])

app.logger.info('Service terminated')
