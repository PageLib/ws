# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import ConcreteBase
from datetime import datetime
from app import db
from uuid import uuid4
from flask import url_for
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID


class Transaction(ConcreteBase, db.Model):
    """
    Parent class for every transaction.
    """
    __tablename__ = 'transaction'
    id = db.Column(db.CHAR(32), primary_key=True)
    user = db.Column(db.CHAR(32), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.CHAR(3))

    __mapper_args__ = {
        'polymorphic_identity': 'transaction',
        'concrete': True
    }


    def __init__(self, user, amount, currency, date_time=None):
        #TODO gerer les collisions (on fait un truc global?)
        self.id = uuid4().hex
        #TODO Controle des users
        self.user = user
        self.amount = amount
        if date_time is None:
            date_time = datetime.utcnow()
        self.date_time = date_time
        self.currency = currency


    def __repr__(self):
        return '<Transaction {}>'.format(self.id)

    def to_dict(self):
        return {
            'user': self.user,
            'amount': self.amount,
            'date_time': self.date_time,
            'currency': self.currency,
#            'uri': url_for('invoice', self.id)
        }

class Printing(Transaction):
    """
    Records the printings of the users.
    """
    __tablename__ = 'printing'
    id = db.Column(db.CHAR(32), primary_key=True)
    user = db.Column(db.CHAR(32), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    currency = db.Column(db.CHAR(3))
    date_time = db.Column(db.DateTime(), default='')
    pages_color = db.Column(db.Integer)
    pages_grey_level = db.Column(db.Integer)
    copies = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'printing',
        'concrete': True
    }

    def __init__(self, user, amount, pages_color, pages_grey_level, copies, currency, date_time=None):
        self.amount = amount
        self.pages_color = pages_color
        self.pages_grey_level = pages_grey_level
        self.copies = copies
        super(Printing, self).__init__(user, amount, currency, date_time)

    def to_dict(self):
        d = super(Printing, self).to_dict()
        d.update({
            'pages_color': self.pages_color,
            'pages_grey_level': self.pages_grey_level,
            'copies': self.copies
        })
        return d


class LoadingCreditCard(Transaction):
    """
    Records the loadings operations with the credit card made by the user.
    """
    __tablename__ = 'loading_credit_card'

    id = db.Column(db.CHAR(32), primary_key=True)
    user = db.Column(db.CHAR(32), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.CHAR(3))

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

    id = db.Column(db.CHAR(32), primary_key=True)
    user = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_time = db.Column(db.DateTime(), default='')
    currency = db.Column(db.CHAR(3))

    __mapper_args__ = {
        'polymorphic_identity': 'help_desk',
        'concrete': True
    }