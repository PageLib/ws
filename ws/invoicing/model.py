# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app import db
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class Transaction(db.Model):
    """
    Parent class for every transaction.
    """
    __tablename__ = 'transaction'
    id = db.Column(GUID(), primary_key=True)
    user = db.Column(db.CHAR(36), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.CHAR(3))
    type = db.Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'transaction',
        'polymorphic_on': type
    }


def __init__(self, title, amount, date_time):
    self.title = title
    self.currency = 'EUR'
    self.amount = amount
    if date_time is None:
        date_time = datetime.utcnow()
    self.date_time = date_time


def __repr__(self):
    return '<Transaction {}>'.format(self.id)


class Printing(Transaction):
    __tablename__ = 'printing'
    id = db.Column(CHAR(36), ForeignKey('transaction.id'), primary_key=True)
    pages_color = db.Column(db.Integer)
    pages_grey_level = db.Column(db.Integer)
    copies = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'printing',
    }


class Loading_credit_card(Transaction):
    __tablename__ = 'loading_credit_card'

    id = db.Column(CHAR(36), ForeignKey('transaction.id'), primary_key=True)
    # On ne sait pas encore ce qu'on aur comme infos ici.

    __mapper_args__ = {
        'polymorphic_identity': 'loading_credit_card',
    }


class Help_desk(Transaction):
    __tablename__ = 'help_desk'

    id = db.Column(CHAR(36), ForeignKey('transaction.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'help_desk',
    }
