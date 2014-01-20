# -*- coding: utf-8 -*-

import json
import requests
from WsTestCase import WsTestCase


class IamTestCase(WsTestCase):
    ref_user = {
        'login': 'john.doe',
        'password': '1234',
        'last_name': 'Doe',
        'first_name': 'John',
        'role': 'user'
    }

    def assertJsonAndStatus(self, rv, status):
        if rv.text is not None and rv.text != '':
            self.assertEquals(rv.headers['Content-type'], 'application/json')
        self.assertEquals(rv.status_code, status)

    def test_create_user(self):
        """Create and GET a user."""
        rv_post = requests.post(self.iam_endpoint + '/v1/users',
                                data=json.dumps(self.ref_user),
                                headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_post, 201)
        json_post = rv_post.json()

        # check returned user's fields
        for field in ('login', 'last_name', 'first_name', 'role'):
            self.assertIn(field, json_post, 'missing field ' + field)
            self.assertEquals(json_post[field], self.ref_user[field], 'mismatch on field ' + field)

        user_id = json_post['id']

        rv_get = requests.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertJsonAndStatus(rv_get, 200)

    def test_edit_user(self):
        """Create and modify a user."""
        pass

    def test_create_user_twice(self):
        """Try to create the same user twice, assert failure on the second trial."""
        pass

    def test_delete_recreate_user(self):
        """Create and delete a user, assert that the user no longer exists, and can be created
            again."""
        pass

    def test_create_login_logout(self):
        """Create a user and test login and logout actions."""
        pass

    def test_create_login_permission(self):
        """Create a user, login, and test permissions."""
        pass
