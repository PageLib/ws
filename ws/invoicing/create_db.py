import app
import model

model.Base.metadata.create_all(app.db_engine)
