import sys
import model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import hashlib


def create(database_uri):
    """
    Create the database for IAM at database_uri.
    """
    # Prepare database connection
    db_engine = create_engine(database_uri)
    model.Base.metadata.create_all(db_engine)


def create_default_data(database_uri):
    db_engine = create_engine(database_uri)
    dbs = sessionmaker(db_engine)()
    entity_id = uuid.uuid4().hex

    entity = model.Entity(
        id=entity_id,
        name='admin_entity',
        deleted=False
    )
    dbs.add(entity)
    admin = model.User(
        id=uuid.uuid4().hex,
        login='admin',
        password_hash=hashlib.sha1('1234').hexdigest(),
        role='admin',
        deleted=False,
        entity_id=entity_id
    )
    dbs.add(admin)
    dbs.commit()


if __name__ == '__main__':
    create(sys.argv[1])
    create_default_data(sys.argv[1])
