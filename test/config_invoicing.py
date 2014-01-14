"""Configuration for Invoicing service in testing mode."""

HOST = '127.0.0.1'
PORT = 5000
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/db_invoicing.sqlite'
CREATE_SCHEMA_ON_STARTUP = True
