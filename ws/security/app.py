# -*- coding: utf-8 -*-

import os
import datetime
import json
from uuid import uuid4
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import model
import user_data

app = Flask(__name__)

# Load configuration
config_path = os.environ.get('PAGELIB_WS_SECURITY_CONFIG', 'config')
app.config.from_object(config_path)

# Prepare database connection
db_engine = create_engine(app.config['DATABASE_URI'])
DBSession = sessionmaker(db_engine)


@app.route('/login', methods=['POST'])
def login_action():
    # Get credentials passed in the request
    data = request.get_json()
    login = data['login']
    password = data['password']

    # Find a matching user
    matches = filter(lambda u: u['login'] == login and u['password'] == password, user_data.users)
    if len(matches) != 1:
        return '', 412
    user = matches[0]

    # Close existing sessions for this user
    dbs = DBSession()
    opened_sessions = dbs.query(model.Session).filter(model.Session.user_id == user['id']).all()
    for s in opened_sessions:
        dbs.delete(s)

    # Open the session
    session = model.Session(
        id=uuid4().hex,
        user_id=user['id'],
        opened=datetime.datetime.now(),
        refreshed=datetime.datetime.now(),
        role=user['role']
    )
    dbs.add(session)
    dbs.commit()

    # Return session data
    resp_data = {
        'user_id': user['id'],
        'session_id': session.id
    }
    return json.dumps(resp_data), 200, {'Content-type': 'application/json'}


@app.route('/sessions/<session_id>/logout', methods=['POST'])
def logout_action(session_id):
    dbs = DBSession()
    try:
        # Find and delete the session
        session = dbs.query(model.Session).filter(model.Session.id == session_id).one()
        dbs.delete(session)
        dbs.commit()

        return json.dumps({'result': 'success'}), 200, {'Content-type': 'application/json'}

    except NoResultFound:
        return '', 404

    except MultipleResultsFound:
        # TODO: log something
        return '', 500


@app.route('/sessions/<session_id>', methods=['GET'])
def session_info_action(session_id):
    pass


@app.route('/sessions/<session_id>/permission/<action>/<resource>', methods=['GET'])
def session_permission_action(session_id, action, resource):
    pass


if __name__ == '__main__':
    app.run()
