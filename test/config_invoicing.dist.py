"""Configuration for Invoicing service in testing mode."""

import logging

HOST = '127.0.0.1'
PORT = 5000
DEBUG = False

LOG_FILE = ''
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

SQLALCHEMY_DATABASE_URI = 'sqlite:///<file>'
CREATE_SCHEMA_ON_STARTUP = True
