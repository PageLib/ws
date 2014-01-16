"""Configuration for IAM service in testing mode."""

import logging

HOST = '127.0.0.1'
PORT = 6001
DEBUG = False

LOG_FILE = ''
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

DATABASE_URI = 'sqlite:///<file>'
CREATE_SCHEMA_ON_STARTUP = True

SESSION_LIFETIME = 15*60  # in seconds
