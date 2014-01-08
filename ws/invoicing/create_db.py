import model
from sqlalchemy import create_engine

db_engine = create_engine('sqlite:///dev.db')
model.Base.metadata.create_all(db_engine)