# -*- coding: utf-8 -*-

import unittest
import os
import sys
import json
from requests.auth import HTTPBasicAuth
from hashlib import sha1
import requests
from subprocess import Popen, PIPE
import config_iam
import config_invoicing
import time
import ws.iam.schema
import ws.invoicing.schema
from wsc.Configuration import Configuration
from wsc.iam import IAM


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

        self.entity_id = 'bab2ab808f1a11e3baa80800200c9a66'
        self.admin_id = '0f6bf8708f1b11e3baa80800200c9a66'

        self.startup_time = float(os.environ.get('PAGELIB_WS_TEST_STARTUP_TIME', 1))

        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        ws.iam.schema.create(config_iam.DATABASE_URI)
        ws.iam.schema.create_default_data(config_iam.DATABASE_URI)
        ws.invoicing.schema.create(config_invoicing.SQLALCHEMY_DATABASE_URI)

        self.iam_proc = Popen([self.python_cmd, self.ws_root + '/iam/app.py'], stdout=PIPE, stderr=PIPE)
        self.invoicing_proc = Popen([self.python_cmd, self.ws_root + '/invoicing/app.py'], stdout=PIPE, stderr=PIPE)

        config = Configuration()
        config.iam_endpoint = self.iam_endpoint
        config.invoicing_endpoint = self.invoicing_endpoint

        # Wait for services to be ready
        time.sleep(self.startup_time)

        # Login with WSC
        iam = IAM(config)
        self.session = iam.login('admin', sha1('plop_io').hexdigest())

    def tearDown(self):
        self.iam_proc.kill()
        self.invoicing_proc.kill()
        os.remove(config_iam.DATABASE_URI[len('sqlite:///'):])
        os.remove(config_invoicing.SQLALCHEMY_DATABASE_URI[len('sqlite:///'):])

    def post_json(self, url, data, session=None, **kwargs):
        headers = {'Content-type': 'application/json'}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        if session is not None:
            return requests.post(url,
                                 data=json.dumps(data),
                                 headers=headers,
                                 auth=(session.user_id, session.session_id))

        return requests.post(url,
                             data=json.dumps(data),
                             headers=headers)

    def put_json(self, url, data, session=None, **kwargs):
        headers = {'Content-type': 'application/json'}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        if session is not None:
            return requests.put(url,
                                data=json.dumps(data),
                                headers=headers,
                                auth=(session.user_id, session.session_id))

        return requests.put(url,
                            data=json.dumps(data),
                            headers=headers)

    def get(self, url, session=None, **kwargs):
        headers = {}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        if session is None:
            session = self.session
        return requests.get(url,
                            headers=headers,
                            auth=(session.user_id, session.session_id))

    def delete(self, url, session=None, **kwargs):
        headers = {}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        if session is None:
            session = self.session
        return requests.get(url,
                            headers=headers,
                            auth=(session.user_id, session.session_id))