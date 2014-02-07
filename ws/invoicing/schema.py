import sys
import model
from sqlalchemy import create_engine


def create(database_uri):
    """
    Create the database for IAM at database_uri.
    """
    # Prepare database connection
    db_engine = create_engine(database_uri)
    model.Base.metadata.create_all(db_engine)

if __name__ == '__main__':
    create(sys.argv[1])
