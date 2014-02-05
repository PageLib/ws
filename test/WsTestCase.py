# -*- coding: utf-8 -*-

import unittest
import os
import sys
from subprocess import Popen, PIPE
import config_iam
import config_invoicing
import time
import ws.iam.schema
import ws.invoicing.schema


class WsTestCase(unittest.TestCase):
    """
    Base class for webservices test cases.
    Spawns WS processes (with test-specific configurations) on setUp and kills them on tearDown.
    """

    def __init__(self, *args, **kwargs):
        test_root = os.path.dirname(__file__)
        self.ws_root = os.path.dirname(__file__) + '/../ws'
        self.python_cmd = sys.executable

        os.environ['PAGELIB_WS_IAM_CONFIG'] = test_root + '/config_iam.py'
        os.environ['PAGELIB_WS_INVOICING_CONFIG'] = test_root + '/config_invoicing.py'

        self.iam_endpoint = 'http://{}:{}'.format(config_iam.HOST, config_iam.PORT)
        self.invoicing_endpoint = 'http://{}:{}'.format(config_invoicing.HOST, config_invoicing.PORT)

        self.startup_time = float(os.environ.get('PAGELIB_WS_TEST_STARTUP_TIME', 1))

        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        ws.iam.schema.create(config_iam.DATABASE_URI)
        ws.iam.schema.create_default_data(config_iam.DATABASE_URI)
        ws.invoicing.schema.create(config_invoicing.SQLALCHEMY_DATABASE_URI)

        self.iam_proc = Popen([self.python_cmd, self.ws_root + '/iam/app.py'], stdout=PIPE, stderr=PIPE)
        self.invoicing_proc = Popen([self.python_cmd, self.ws_root + '/invoicing/app.py'], stdout=PIPE, stderr=PIPE)

        # Wait for services to be ready
        time.sleep(self.startup_time)

    def tearDown(self):
        self.iam_proc.kill()
        self.invoicing_proc.kill()
        os.remove(config_iam.DATABASE_URI[len('sqlite:///'):])
        os.remove(config_invoicing.SQLALCHEMY_DATABASE_URI[len('sqlite:///'):])
