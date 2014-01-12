from sqlalchemy import create_engine
import ws.iam.model as model
from app import app
db_engine = create_engine(app.config['DATABASE_URI'])
model.Base.metadata.create_all(db_engine)