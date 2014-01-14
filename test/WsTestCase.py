# -*- coding: utf-8 -*-

import unittest
import os
import sys
from subprocess import Popen


class WsTestCase(unittest.TestCase):
    """
    Base class for webservices test cases.
    Spawns WS processes (with test-specific configurations) on setUp and kills them on tearDown.
    """

    def __init__(self):
        test_root = os.path.dirname(__file__)
        self.ws_root = os.path.dirname(__file__) + '/../ws'
        self.python_cmd = sys.executable

        os.environ['PAGELIB_WS_IAM_CONFIG'] = test_root + '/config_iam.py'
        os.environ['PAGELIB_WS_INVOICING_CONFIG'] = test_root + '/config_invoicing.py'

    def setUp(self):
        self.iam_proc = Popen([self.python_cmd, self.ws_root + '/iam/app.py'])
        self.invoicing_proc = Popen([self.python_cmd, self.ws_root + '/invoicing/app.py'])

    def tearDown(self):
        pass
