# -*- coding: utf-8 -*-

"""Template configuration file for IAM webservice."""

import logging

HOST = '127.0.0.1'
PORT = 5002
DEBUG = True

LOG_FILE = ''
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

DATABASE_URI = ''
DOCS_URI = ''
CREATE_SCHEMA_ON_STARTUP = False

INVOICING_ENDPOINT = ''
IAM_ENDPOINT = ''
SETTINGS_ENDPOINT = ''
