"""Configuration for Invoicing service in testing mode."""

import logging

HOST = '127.0.0.1'
PORT = 6000
DEBUG = False

LOG_FILE = ''
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

SQLALCHEMY_DATABASE_URI = 'sqlite:///<file>'
CREATE_SCHEMA_ON_STARTUP = True

IAM_ENDPOINT = ''
DOCS_ENDPOINT = ''
SETTINGS_ENDPOINT = ''
