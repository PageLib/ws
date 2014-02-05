"""Template configuration file for Invoicing webservice."""

import logging

HOST = '127.0.0.1'
PORT = 5000
DEBUG = False

LOG_FILE = ''
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

SQLALCHEMY_DATABASE_URI = ''

IAM_ENDPOINT = ''
DOCS_ENDPOINT = ''
SETTINGS_ENDPOINT = ''
