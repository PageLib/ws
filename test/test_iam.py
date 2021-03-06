# -*- coding: utf-8 -*-

import json
import requests
import hashlib
from WsTestCase import WsTestCase


class IamTestCase(WsTestCase):
    ref_user = {
        'login': 'john.doe',
        'password_hash': '1234',
        'last_name': 'Doe',
        'first_name': 'John',
        'role': 'user',
        'entity_id': 'bab2ab808f1a11e3baa80800200c9a66'
    }

    def test_create_user_twice(self):
        """Try to create the same user twice, the first works and we assert failure on the second trial."""
        rv_post = self.post_json(self.iam_endpoint + '/v1/users',
                                 self.ref_user,
                                 self.session)
        self.assertJsonAndStatus(rv_post, 201)
        json_post = rv_post.json()

        # check returned user's fields
        for field in ('login', 'last_name', 'first_name', 'role', 'entity_id'):
            self.assertIn(field, json_post, 'missing field ' + field)
            self.assertEquals(json_post[field], self.ref_user[field], 'mismatch on field ' + field)

        user_id = json_post['id']

        rv_get = self.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertJsonAndStatus(rv_get, 200)

        rv_post_2 = self.post_json(self.iam_endpoint + '/v1/users',
                                   self.ref_user,
                                   self.session)
        self.assertJsonAndStatus(rv_post_2, 412)

    def test_edit_user(self):
        """Create and modify a user."""
        rv_post = self.post_json(self.iam_endpoint + '/v1/users',
                                 self.ref_user,
                                 self.session)
        user_id = rv_post.json()['id']

        put_data = {
            'login': 'jack.foo',
            'last_name': 'Foo',
            'first_name': 'Jack',
            'role': 'manager'
        }

        # Edit the user
        rv_put = self.put_json(self.iam_endpoint + '/v1/users/' + user_id,
                               put_data,
                               self.session)
        self.assertJsonAndStatus(rv_put, 200)
        json_put = rv_put.json()

        # Get it
        rv_get = self.get(self.iam_endpoint + '/v1/users/' + user_id)
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
        rv_create = self.post_json(self.iam_endpoint + '/v1/users',
                                   self.ref_user,
                                   self.session)
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        rv_delete = self.delete(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertJsonAndStatus(rv_delete, 200)

        rv_get = self.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertEquals(rv_get.status_code, 404)

        rv_recreate = self.post_json(self.iam_endpoint + '/v1/users',
                                     self.ref_user,
                                     self.session)
        self.assertJsonAndStatus(rv_recreate, 201)

    def test_create_login_permission_logout(self):
        """Create a user, login, test permissions, and logout."""
        rv_create = self.post_json(self.iam_endpoint + '/v1/users',
                                   self.ref_user,
                                   self.session)
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        # Log in with bad password
        rv_login_failed = self.post_json(
            self.iam_endpoint + '/v1/login',
            {'login': self.ref_user['login'],
             'password_hash': hashlib.sha1('qwerty').hexdigest()},
            self.session)
        self.assertEquals(rv_login_failed.status_code, 404)

        # Log in
        rv_login = self.post_json(
            self.iam_endpoint + '/v1/login',
            {'login': self.ref_user['login'],
             'password_hash': hashlib.sha1(self.ref_user['password_hash']).hexdigest()},
            self.session)
        self.assertJsonAndStatus(rv_login, 200)
        session_id = rv_login.json()['session_id']

        # Check a granted permission
        rv_permission_1 = self.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'read', 'own_transaction'
            ))
        self.assertJsonAndStatus(rv_permission_1, 200)
        self.assertTrue(rv_permission_1.json()['allowed'])

        # Check a denied permission
        rv_permission_2 = self.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'read', 'transaction'
            ))
        self.assertJsonAndStatus(rv_permission_1, 200)
        self.assertFalse(rv_permission_2.json()['allowed'])

        # Check a non-existing permission
        rv_permission_3 = self.get(
            self.iam_endpoint + '/v1/sessions/{}/{}/permission/{}/{}'.format(
                user_id, session_id, 'dummy', 'dummy'
            ))
        self.assertEquals(404, rv_permission_3.status_code)

        # Log out
        rv_logout = self.post_json(self.iam_endpoint + '/v1/sessions/' + session_id + '/logout',
                                   self.session)
        self.assertEquals(200, rv_logout.status_code)

        # Check that the session no longer exists
        rv_session = self.get(self.iam_endpoint + '/v1/sessions/' + session_id)
        self.assertEquals(404, rv_session.status_code)

    def test_search(self):
        """ Create an entity with a user in it, search the user twice:
        * first find him
        * second don't find him
        """
        # Create
        rv_create = self.post_json(self.iam_endpoint + '/v1/users',
                                   self.ref_user,
                                   self.session)
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        # Find him
        rv_search_find = self.get(self.iam_endpoint + '/v1/users?login=john.doe')
        users = rv_search_find.json()['users']
        self.assertEquals(1, len(users))
        self.assertEquals(user_id, users[0]['id'])

        # Doesn't
        rv_search_not_found = self.get(self.iam_endpoint + '/v1/users?first_name=alex')
        no_user = rv_search_not_found.json()['users']
        self.assertEquals(0, len(no_user))

    def test_put_delete_entity(self):
        """
        Create an entity, PUT it, add a user delete the entity and check that the user is deleted.
        """

        # Edit the entity, then get it and assert the name was modified
        entity_id = self.ref_user['entity_id']
        rv_put = self.put_json(self.iam_endpoint + '/v1/entities/' + entity_id,
                               {'name': 'Centrale-Supelec'},
                               self.session)
        self.assertJsonAndStatus(rv_put, 200)

        rv_get_entity = self.get(self.iam_endpoint + '/v1/entities/' + entity_id)
        self.assertJsonAndStatus(rv_get_entity, 200)
        self.assertEquals('Centrale-Supelec', rv_get_entity.json()['name'])

        # Add a user
        rv_create = self.post_json(self.iam_endpoint + '/v1/users',
                                   self.ref_user,
                                   self.session)
        self.assertJsonAndStatus(rv_create, 201)
        user_id = rv_create.json()['id']

        # Delete the entity and assert the user no longer exists
        rv_delete = self.delete(self.iam_endpoint + '/v1/entities/' + entity_id)
        self.assertEquals(200, rv_delete.status_code)

        rv_get_user = self.get(self.iam_endpoint + '/v1/users/' + user_id)
        self.assertEquals(404, rv_get_user.status_code)
