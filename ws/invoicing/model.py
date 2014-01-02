# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import ConcreteBase
from datetime import datetime
from app import db
import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID


# class GUID(TypeDecorator):
#     """Platform-independent GUID type.
#
#     Uses Postgresql's UUID type, otherwise uses
#     CHAR(32), storing as stringified hex values.
#
#     """
#     impl = CHAR
#
#     def load_dialect_impl(self, dialect):
#         if dialect.name == 'postgresql':
#             return dialect.type_descriptor(UUID())
#         else:
#             return dialect.type_descriptor(CHAR(32))
#
#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return value
#         elif dialect.name == 'postgresql':
#             return str(value)
#         else:
#             if not isinstance(value, uuid.UUID):
#                 return "%.32x" % uuid.UUID(value)
#             else:
#                 # hexstring
#                 return "%.32x" % value
#
#     def process_result_value(self, value, dialect):
#         if value is None:
#             return value
#         else:
#             return uuid.UUID(value)


class Transaction(ConcreteBase, db.Model):
    """
    Parent class for every transaction.
    """
    __tablename__ = 'transaction'
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.String(3))

    __mapper_args__ = {
        'polymorphic_identity': 'transaction',
        'concrete': True
    }


    def __init__(self, user, amount, date_time=None):
        self.user = user
        self.amount = amount
        if date_time is None:
            date_time = datetime.utcnow()
        self.date_time = date_time
        self.currency = 'EUR'


    def __repr__(self):
        return '<Transaction {}>'.format(self.id)

    def to_dict(self):
        return {
            'user': self.user,
            'amount': self.amount,
            'date_time': self.date_time,
            'currency': self.currency
        }

class Printing(Transaction):
    """
    Records the printings of the users.
    """
    __tablename__ = 'printing'
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.String(3))
    pages_color = db.Column(db.Integer)
    pages_grey_level = db.Column(db.Integer)
    copies = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'printing',
        'concrete': True
    }

    def to_dict(self):
        return {
            'user': self.user,
            'amount': self.amount,
            'date_time': self.date_time,
            'currency': self.currency,
            'pages_color': self.pages_color,
            'pages_grey_level': self.pages_grey_level,
            'copies': self.copies
        }


class LoadingCreditCard(Transaction):
    """
    Records the loadings operations with the credit card made by the user.
    """
    __tablename__ = 'loading_credit_card'

    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.String(3))

    # On ne sait pas encore ce qu'on aura comme infos ici.

    __mapper_args__ = {
        'polymorphic_identity': 'loading_credit_card',
        'concrete': True
    }


class HelpDesk(Transaction):
    """
    Records the operations made by the help desk.
    """
    __tablename__ = 'help_desk'

    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.String(3))

    __mapper_args__ = {
        'polymorphic_identity': 'help_desk',
        'concrete': True
    }