"""Configuration for IAM service in testing mode."""

HOST = '127.0.0.1'
PORT = 5001
DEBUG = False
DATABASE_URI = 'sqlite:///:memory:'
SESSION_LIFETIME = 15*60  # in seconds
