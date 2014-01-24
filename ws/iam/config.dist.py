# -*- coding: utf-8 -*-

"""Template configuration file for IAM webservice."""

import logging

HOST = '127.0.0.1'
PORT = 5001
DEBUG = True

LOG_FILE = ''
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'

DATABASE_URI = ''
CREATE_SCHEMA_ON_STARTUP = False

SESSION_LIFETIME = 15*60  # in seconds
