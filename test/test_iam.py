# -*- coding: utf-8 -*-

import os
import unittest
from sqlalchemy import create_engine

os.environ['PAGELIB_WS_IAM_CONFIG'] = os.path.dirname(__file__) + '/config_test.py'
import ws.iam.app as iam_app
import ws.iam.model as model


class IamTestCase(unittest.TestCase):
    def setUp(self):
        self.app = iam_app.app.test_client()
        db_engine = create_engine(self.app.config['DATABASE_URI'])
        model.Base.metadata.create_all(db_engine)

    def tearDown(self):
        model.Base.metadata.drop_all(iam_app.db_engine)

    def assertJsonContentType(self, rv):
        self.assertEquals(rv.headers['Content-type'], 'application/json')

    def test_login_successful(self):
        """
        Logs in a user successfully and checks that
        """
        user_id = '0dae86f391b940ada87080c43a9ec441'
        password = '1234'
        rv = self.app.post('/login')


