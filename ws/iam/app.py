# -*- coding: utf-8 -*-

import os
import datetime
from uuid import uuid4
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from ws.common.decorators import json_response
import model
import user_data
from roles import acl

app = Flask(__name__)

# Load configuration
config_path = os.environ.get('PAGELIB_WS_SECURITY_CONFIG', 'config')
app.config.from_object(config_path)

# Prepare database connection
db_engine = create_engine(app.config['DATABASE_URI'])
DBSession = sessionmaker(db_engine)


@app.route('/login', methods=['POST'])
@json_response
def login_action():
    # Get credentials passed in the request
    data = request.get_json()
    user_id = data['user_id']
    password = data['password']

    # Find a matching user
    matches = filter(lambda u: u['id'] == user_id and u['password'] == password, user_data.users)
    if len(matches) != 1:
        return '', 412
    user = matches[0]

    # Close existing sessions for this user
    dbs = DBSession()
    opened_sessions = dbs.query(model.Session).filter(model.Session.user_id == user_id).all()
    for s in opened_sessions:
        dbs.delete(s)

    # Open the session
    session = model.Session(
        id=uuid4().hex,
        user_id=user_id,
        opened=datetime.datetime.now(),
        refreshed=datetime.datetime.now(),
        role=user['role']
    )
    dbs.add(session)
    dbs.commit()

    # Return session data
    resp_data = {
        'user_id': user_id,
        'session_id': session.id
    }
    return resp_data, 200


@app.route('/sessions/<session_id>/logout', methods=['POST'])
@json_response
def logout_action(session_id):
    dbs = DBSession()
    try:
        # Find and delete the session
        session = dbs.query(model.Session).filter(model.Session.id == session_id).one()
        dbs.delete(session)
        dbs.commit()

        return {'result': 'success'}, 200

    except NoResultFound:
        return '', 404

    except MultipleResultsFound:
        # TODO: log something
        return '', 500


@app.route('/sessions/<session_id>', methods=['GET'])
@json_response
def session_info_action(session_id):
    dbs = DBSession()

    try:
        # Find the session
        session = dbs.query(model.Session).filter(model.Session.id == session_id).one()
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


@app.route('/sessions/<session_id>/permission/<action>/<resource>/user/<user_id>', methods=['GET'])
@json_response
def check_permission_action(session_id, action, resource, user_id):
    dbs = DBSession()

    try:
        session = dbs.query(model.Session).filter(model.Session.id == session_id)\
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
    app.run()
