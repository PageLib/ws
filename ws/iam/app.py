# -*- coding: utf-8 -*-

import os
import sys
import datetime
import logging
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from ws.common.decorators import json_response
import model
from roles import acl
from flask_restful import Api
from UserAPI import UserAPI
from UserListAPI import UserListAPI
from ws.common.helpers import generate_uuid_for
import hashlib


app = Flask(__name__)

# Load configuration
config_path = os.environ.get('PAGELIB_WS_IAM_CONFIG',
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
db_engine = create_engine(app.config['DATABASE_URI'])
DBSession = sessionmaker(db_engine)

# Import of the database
@app.before_request
def open_session():
    setattr(request, 'dbs', DBSession())


@app.after_request
def commit_session(response):
    request.dbs.commit()
    return response

if app.config['CREATE_SCHEMA_ON_STARTUP']:
    print 'Creating database schema'
    model.Base.metadata.create_all(db_engine)

api = Api(app)
api.add_resource(UserAPI, '/v1/users/<user_id>', endpoint='user')
api.add_resource(UserListAPI, '/v1/users', endpoint='users')

@app.route('/login', methods=['POST'])
@json_response
def login_action():
    # Get credentials passed in the request
    data = request.get_json()
    try:
        login = data['login']
        password_hash = data['password_hash']
    except KeyError:
        return {'error': 'Missing Keyword \'login\' or \'password\' in json'}, 412

    # Find a matching user
    try:
        user = request.dbs.query(model.User).filter(model.User.login == login).\
                                            filter(model.User.password_hash == password_hash).one()
    except NoResultFound:
        return {}, 404

    except MultipleResultsFound:
        # TODO: log something
        return {}, 500

    opened_sessions = request.dbs.query(model.Session).filter(model.Session.user_id == user.id).all()
    for s in opened_sessions:
        request.dbs.delete(s)

    # Open the session
    session = model.Session(
        id=generate_uuid_for(request.dbs, model.Session),
        user_id=user.id,
        opened=datetime.datetime.now(),
        refreshed=datetime.datetime.now(),
        role=user.role
    )
    request.dbs.add(session)

    # Return session data
    resp_data = {
        'login': login,
        'session_id': session.id
    }
    return resp_data, 200


@app.route('/sessions/<session_id>/logout', methods=['POST'])
@json_response
def logout_action(session_id):
    try:
        # Find and delete the session
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id).one()
        request.dbs.delete(session)

        return {'result': 'success'}, 200

    except NoResultFound:
        return '', 404

    except MultipleResultsFound:
        # TODO: log something
        return '', 500


@app.route('/sessions/<user_id>/<session_id>', methods=['GET'])
@json_response
def session_info_action(session_id, user_id):
    try:
        # Find the session
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id).\
                                           filter(model.Session.user_id == user_id).one()
        resp_data = {
            'session_id': session.id,
            'user_id': session.user_id,
            'opened': session.opened.isoformat(),
            'refreshed': session.refreshed.isoformat(),
            'expires': session.expires.isoformat()
        }
        return resp_data, 200

    except NoResultFound:
        return '', 404

    except MultipleResultsFound:
        # TODO: log something
        return '', 500


@app.route('/sessions/<user_id>/<session_id>/permission/<action>/<resource>', methods=['GET'])
@json_response
def check_permission_action(session_id, action, resource, user_id):
    try:
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id)\
                                          .filter(model.Session.user_id == user_id).one()
        return {'allowed': acl.is_allowed(session.role, action, resource)}, 200

    except NoResultFound:
        return '', 404

    except MultipleResultsFound:
        # TODO: log something
        return '', 500

    except AssertionError:
        # action or resource not declared
        return '', 404


if __name__ == '__main__':
    app.logger.info('Starting service')
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])

app.logger.info('Service terminated')
