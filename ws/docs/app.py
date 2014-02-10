# -*- coding: utf8 -*-

import os
import sys
import logging
from flask import Flask, request, abort, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from ws.common.MyAPI import MyApi
from wsc.iam import IAM, Session
from wsc.Configuration import Configuration
import model

app = Flask(__name__)

from DocumentAPI import DocumentAPI
from DocumentListAPI import DocumentListAPI
from DocumentRawAPI import DocumentRawAPI

# Load configuration
config_path = os.environ.get('PAGELIB_WS_DOCS_CONFIG',
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

if app.config['CREATE_SCHEMA_ON_STARTUP']:
    app.logger.info('Creating database schema')
    model.Base.metadata.create_all(db_engine)

# Set up WSC configuration
wsc_config = Configuration()
wsc_config.docs_endpoint = 'http://{}:{}'.format(app.config['HOST'], app.config['PORT'])
wsc_config.invoicing_endpoint =app.config['INVOICING_ENDPOINT']
wsc_config.iam_endpoint = app.config['INVOICING_ENDPOINT']
wsc_config.settings_endpoint = app.config['SETTINGS_ENDPOINT']

@app.before_request
def open_session():
    setattr(request, 'dbs', DBSession())
    setattr(request, 'wsc_config', wsc_config)
    setattr(request, 'iam', IAM(wsc_config))

    # Retrieve WS session attributes
    auth = request.authorization
    if auth:
        setattr(request, 'ws_session', Session(auth.username, auth.password))
    else:
        setattr(request, 'ws_session', Session(None, None))


@app.after_request
def commit_session(response):
    request.dbs.commit()
    return response

# Set up RESTful API resources
api = MyApi(app)
api.add_resource(DocumentListAPI, '/v1/docs', endpoint='docs')
api.add_resource(DocumentAPI, '/v1/docs/<string:id>', endpoint='doc')
api.add_resource(DocumentRawAPI, '/v1/docs/<string:doc_id>/raw', endpoint='doc_raw')

@app.route('/v1/docs/<string:doc_id>/raw', methods=['GET'])
def get_doc_raw(doc_id):
    try:
        doc = request.dbs.query(model.Document).filter(model.Document.id == doc_id).one()
        path = app.config['DOCS_URI']
        doc_name = doc.name + '.pdf'
        if os.access(path, os.R_OK):
            return send_from_directory(path, doc_id + '.pdf', attachment_filename=doc_name, as_attachment=True)

    except NoResultFound:
        app.logger.warning('Request on non existing document ' + doc_id)
        abort(404)
    except IOError:
        app.logger.warning('Request on non existing raw document ' + doc_id)
        abort(404)
    except MultipleResultsFound:
        app.logger.error('Multiple results found for document ' + doc_id)
        abort(500)


if __name__ == '__main__':
    app.logger.info('Starting service')
    app.run(host=app.config['HOST'], port=app.config['PORT'])

app.logger.info('Service terminated')
