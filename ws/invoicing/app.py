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
api.add_resource(InvoicingListAPI, '/v1/invoices', endpoint='invoices')

from invoicingAPI import InvoicingAPI
api.add_resource(InvoicingAPI, '/v1/invoices/<string:id>', endpoint='invoice')

from balanceAPI import BalanceAPI
api.add_resource(BalanceAPI, '/v1/user/balance/<string:id>', endpoint='balance')