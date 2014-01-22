from uuid import uuid4
from sqlalchemy import exists
from flask import abort


def generate_uuid_for(dbs, db_class):
    new_id = uuid4().hex
    while dbs.query(exists().where(db_class.id == new_id)).scalar():
        new_id = uuid4().hex
    return new_id


def get_or_412(args, name):
    if args.get(name, None):
        return args.get(name, None)
    else:
        error = 'No ' + name + ' provided'
        abort(412, error)
