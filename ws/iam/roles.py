# -*- coding: utf-8 -*-

from rbac.acl import Registry

acl = Registry()

roles = ['admin', 'user', 'manager']

for role in roles:
    acl.add_role(role)

# Accounts resources
acl.add_resource('user')
acl.add_resource('own_user')
for u in ['user', 'own_user']:
    acl.allow('admin', 'read', u)
    acl.allow('admin', 'update', u)
    acl.allow('admin', 'delete', u)
acl.allow('admin', 'create', 'user')
acl.allow('user', 'read', 'own_user')
acl.allow('user', 'update', 'own_user')
acl.allow('user', 'delete', 'own_user')

# Invoicing
acl.add_resource('transaction')
acl.add_resource('own_transaction')
for t in ['transaction', 'own_transaction']:
    acl.allow('admin', 'read', t)
    acl.allow('admin', 'create', t)
acl.allow('user', 'read', 'own_transaction')
acl.allow('user', 'create', 'own_transaction')


# Documents resources
# ...