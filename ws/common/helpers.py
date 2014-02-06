from uuid import uuid4
from sqlalchemy import exists
from flask import request, abort
from wsc.exc import Unauthorized


def generate_uuid_for(dbs, db_class):
    new_id = uuid4().hex
    while dbs.query(exists().where(db_class.id == new_id)).scalar():
        new_id = uuid4().hex
    return new_id


def is_allowed(action, resource):
    """Check a permission using the WS context stored in the request."""
    if hasattr(request, 'ws_session') and hasattr(request, 'iam'):
        return request.iam.is_allowed(request.ws_session, action, resource)
    else:
        return False


def ensure_allowed(action, resource):
    """Ensure a permission (or abort with 403) using the WS context stored in the request."""
    if hasattr(request, 'ws_session') and hasattr(request, 'iam'):
        try:
            request.iam.ensure_allowed(request.ws_session, action, resource)
        except Unauthorized:
            abort(403)


def get_or_412(args, name):
    if args.get(name, None):
        return args.get(name, None)
    else:
        error = 'No ' + name + ' provided'
        abort(412, error)
