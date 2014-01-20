# -*- coding: utf-8 -*-

from WsTestCase import WsTestCase


class IamTestCase(WsTestCase):
    def assertJsonContentType(self, rv):
        self.assertEquals(rv.headers['Content-type'], 'application/json')

    def test_create_user(self):
        """Create and GET a user."""
        pass

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
