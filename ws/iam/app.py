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
from sqlalchemy import not_


app = Flask(__name__)

from UserAPI import UserAPI
from UserListAPI import UserListAPI
from EntityListAPI import EntityListAPI
from EntityAPI import EntityAPI
from ws.common.helpers import generate_uuid_for, get_or_412


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
api.add_resource(EntityAPI, '/v1/entities/<entity_id>', endpoint='entitie')
api.add_resource(EntityListAPI, '/v1/entities', endpoint='entities')


@app.route('/v1/login', methods=['POST'])
@json_response
def login_action():
    # Get credentials passed in the request
    data = request.get_json()
    login = get_or_412(data, 'login')
    password_hash = get_or_412(data, 'password_hash')

    # Find a matching user
    try:
        user = request.dbs.query(model.User).filter(model.User.login == login)\
                                            .filter(model.User.password_hash == password_hash)\
                                            .filter(not_(model.User.deleted)).one()
    except NoResultFound:
        app.logger.warning('Try to log unsuccessfully for user login {}'.format(login))
        return {}, 404

    except MultipleResultsFound:
        app.logger.error('Multiple results on query for user: {} and password_hash: {} in /v1/login'.format(login, password_hash))
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
        'user_id': user.id,
        'session_id': session.id
    }
    app.logger.info('User {} (uuid: {}) logged in session {}'.format(login, user.id,  session.id))
    return resp_data, 200


@app.route('/v1/sessions/<session_id>/logout', methods=['POST'])
@json_response
def logout_action(session_id):
    try:
        # Find and delete the session
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id).one()
        request.dbs.delete(session)
        app.logger.info('Session {} finished.'.format(session_id))
        return {'result': 'success'}, 200

    except NoResultFound:
        app.logger.warning('Try to log out on non existing session: {} in v1:logout'.format(session_id))
        return '', 404

    except MultipleResultsFound:
        app.logger.error('Multiple results found on query for session with id:{} in v1:logout'.format(session_id))
        return '', 500


@app.route('/v1/sessions/<user_id>/<session_id>', methods=['GET'])
@json_response
def session_info_action(session_id, user_id):
    try:
        # Find the session
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id)\
                                                  .filter(not_(model.User.deleted))\
                                                  .filter(model.User.id == model.Session.user_id)\
                                                  .filter(model.Session.user_id == user_id).one()

        # Check that the session is still active
        if not session.is_active:
            app.logger.info('Session {} expired, unable to get session data'.format(session_id))
            return '', 404

        resp_data = {
            'session_id': session.id,
            'user_id': session.user_id,
            'opened': session.opened.isoformat(),
            'refreshed': session.refreshed.isoformat(),
            'expires': session.expires.isoformat()
        }
        app.logger.info('Informed about session {} for user {}'.format(session_id, user_id))
        return resp_data, 200

    except NoResultFound:
        app.logger.warning('Try to check NON existing session {} for user {}'.format(session_id, user_id))
        return '', 404

    except MultipleResultsFound:
        app.logger.error('Multiple results found on query for session with session:{} and user:{}in v1:logout'.format(session_id, user_id))
        return '', 500


@app.route('/v1/sessions/<user_id>/<session_id>/permission/<action>/<resource>', methods=['GET'])
@json_response
def check_permission_action(session_id, action, resource, user_id):
    try:
        session = request.dbs.query(model.Session).filter(model.Session.id == session_id)\
                                                  .filter(model.Session.user_id == user_id)\
                                                  .filter(model.User.id == model.Session.user_id)\
                                                  .filter(not_(model.User.deleted)).one()

        # Check that the session is still active
        if not session.is_active:
            app.logger.info('Session {} expired, unable to check permission'.format(session_id))
            return '', 404

        # Refresh the session
        session.refreshed = datetime.datetime.now()

        # Check permission
        allowed = bool(acl.is_allowed(session.role, action, resource))
        app.logger.info('Permission {} for action {} on {} for user {} in session {}'.format(
            'granted' if allowed else 'denied', action, resource, user_id, session_id))
        return {'allowed': allowed}, 200

    except NoResultFound:
        app.logger.warning('No result found for user {} and session {}').format(user_id, session_id)
        return '', 404

    except MultipleResultsFound:
        app.logger.error('Multiple results found for user {} and session {}').format(user_id, session_id)
        return '', 500

    except AssertionError:
        app.logger.error('Request on non existing resource: {} or action: {}'.format(resource, action))
        return '', 404


@app.route('/v1/sessions/expired', methods=['DELETE'])
@json_response
def delete_expired_sessions_action():
    # Request to be made from local server only
    if request.remote_addr not in ('127.0.0.1', '::1'):
        app.logger.error('Refused request to delete expired sessions from external IP ' + request.remote_addr)
        return '', 404

    sessions = request.dbs.query(model.Session).all()

    for session in sessions:
        if not session.is_active:
            request.dbs.delete(session)
            app.logger.info('Deleted expired session {} (user id {})'.format(session.id,
                                                                             session.user_id))

    return '', 200


if __name__ == '__main__':
    app.logger.info('Starting service')
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])

app.logger.info('Service terminated')
