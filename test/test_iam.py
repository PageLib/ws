# -*- coding: utf-8 -*-

import json
import requests
import hashlib
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
        self.assertEquals(rv.headers['Content-type'], 'application/json')
        self.assertEquals(status, rv.status_code)

    def test_create_user_twice(self):
        """Try to create the same user twice, the first works and we assert failure on the second trial."""
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

        rv_post_2 = requests.post(self.iam_endpoint + '/v1/users',
                                  data=json.dumps(self.ref_user),
                                  headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_post_2, 412)

    def test_edit_user(self):
        """Create and modify a user."""
        rv_post = requests.post(self.iam_endpoint + '/v1/users',
                                data=json.dumps(self.ref_user),
                                headers={'Content-type': 'application/json'})
        user_id = rv_post.json()['id']

        put_data = {
            'login': 'jack.foo',
            'last_name': 'Foo',
            'first_name': 'Jack',
            'role': 'manager'
        }

        # Edit the user
        rv_put = requests.put(self.iam_endpoint + '/v1/users/' + user_id,
                              data=json.dumps(put_data),
                              headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_put, 200)
        json_put = rv_put.json()

        # Get it
        rv_get = requests.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertJsonAndStatus(rv_get, 200)
        json_get = rv_get.json()

        # Assert the concerned fields are modified in both the PUT and GET responses
        for field in ('login', 'last_name', 'first_name', 'role'):
            self.assertIn(field, json_put, 'missing field ' + field + ' in PUT response')
            self.assertIn(field, json_get, 'missing field ' + field + ' in GET response')
            self.assertEquals(json_put[field], put_data[field],
                              'mismatch on field ' + field + ' in PUT response')
            self.assertEquals(json_get[field], put_data[field],
                              'mismatch on field ' + field + ' in GET response')

    def test_delete_recreate_user(self):
        """Create and delete a user, assert that the user no longer exists, and can be created
            again."""
        rv_create = requests.post(self.iam_endpoint + '/v1/users',
                                  data=json.dumps(self.ref_user),
                                  headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        rv_delete = requests.delete(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertJsonAndStatus(rv_delete, 200)

        rv_get = requests.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertEquals(rv_get.status_code, 404)

        rv_recreate = requests.post(self.iam_endpoint + '/v1/users',
                                    data=json.dumps(self.ref_user),
                                    headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_recreate, 201)

    def test_create_login_permission_logout(self):
        """Create a user, login, test permissions, and logout."""
        rv_create = requests.post(self.iam_endpoint + '/v1/users',
                                  data=json.dumps(self.ref_user),
                                  headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        # Log in with bad password
        rv_login_failed = requests.post(
            self.iam_endpoint + '/v1/login',
            data=json.dumps({'login': self.ref_user['login'],
                             'password_hash': hashlib.sha1('qwerty').hexdigest()}),
            headers={'Content-type': 'application/json'})
        self.assertEquals(rv_login_failed.status_code, 404)

        # Log in
        rv_login = requests.post(
            self.iam_endpoint + '/v1/login',
            data=json.dumps({'login': self.ref_user['login'],
                             'password_hash': hashlib.sha1(self.ref_user['password']).hexdigest()}),
            headers={'Content-type': 'application/json'})
        self.assertJsonAndStatus(rv_login, 200)
        session_id = rv_login.json()['session_id']

        # Check a granted permission
        rv_permission_1 = requests.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'read', 'own_transaction'
            ))
        self.assertJsonAndStatus(rv_permission_1, 200)
        self.assertTrue(rv_permission_1.json()['allowed'])

        # Check a denied permission
        rv_permission_2 = requests.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'read', 'transaction'
            ))
        self.assertJsonAndStatus(rv_permission_1, 200)
        self.assertFalse(rv_permission_2.json()['allowed'])

        # Check a non-existing permission
        rv_permission_3 = requests.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'dummy', 'dummy'
            ))
        self.assertEquals(404, rv_permission_3.status_code)

        # Log out
        rv_logout = requests.post(self.iam_endpoint + '/v1/sessions/{}/logout'.format(session_id))
        self.assertEquals(200, rv_logout.status_code)

        # Check that the session no longer exists
        rv_session = requests.get(self.iam_endpoint + '/v1/sessions/' + session_id)
        self.assertEquals(404, rv_session.status_code)
