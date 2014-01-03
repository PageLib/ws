#!flask/bin/python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

config_obj = os.environ.get("PAGELIB_WS_INVOICING_CONFIG", "config_dev")

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(config_obj)

api = Api(app)

from invoicingListAPI import InvoicingListAPI
api.add_resource(InvoicingListAPI, '/v1/invoices', endpoint='invoice')

if __name__ == '__main__':
    app.run(debug=True)