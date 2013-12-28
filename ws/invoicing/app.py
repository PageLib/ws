#!flask/bin/python
# -*- coding: utf-8 -*-
import os
from flask import Flask, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

config_obj = os.environ.get("PAGELIB_WS_INVOICING_CONFIG", "config_dev")

app = Flask(__name__)
app.config.from_object(config_obj)

api = Api(app)
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)