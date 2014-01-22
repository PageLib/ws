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