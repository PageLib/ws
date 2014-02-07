import sys
import model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
    entity_id = 'bab2ab808f1a11e3baa80800200c9a66'

    entity = model.Entity(
        id=entity_id,
        name='admin_entity',
        deleted=False
    )
    dbs.add(entity)

    admin = model.User(
        id='0f6bf8708f1b11e3baa80800200c9a66',
        login='admin',
        password_hash=hashlib.sha1('plop_io').hexdigest(),
        role='admin',
        deleted=False,
        entity_id=entity_id
    )
    dbs.add(admin)
    dbs.commit()

if __name__ == '__main__':
    create(sys.argv[1])
    create_default_data(sys.argv[1])
