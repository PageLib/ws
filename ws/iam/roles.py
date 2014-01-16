# -*- coding: utf-8 -*-

from rbac.acl import Registry

acl = Registry()

roles = ['admin', 'user', 'manager']

for role in roles:
    acl.add_role(role)

# Accounts resources
# ...

# Invoicing
acl.add_resource('transaction')
acl.add_resource('own_transaction')
acl.allow('admin', 'read', 'transaction')
acl.allow('manager', 'read', 'transaction')
acl.allow('user', 'read', 'own_transaction')
acl.allow('user', 'create', 'own_transaction')

# Documents resources
# ...


def check_role(role):
    """
    This part allows us to check if the posted role is correct or not.
    """
    if role in roles or role is None:
        return True
    return False