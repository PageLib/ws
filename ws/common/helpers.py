from uuid import uuid4
from sqlalchemy import exists


def generate_uuid_for(dbs, db_class):
    new_id = uuid4().hex
    while dbs.query(exists().where(db_class.id == new_id)).scalar():
        new_id = uuid4().hex
    return new_id
