# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, CHAR, String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
import fields

Base = declarative_base()

class Transaction(Base):
    """
    Parent class for every transaction.
    """
    __tablename__ = 'transaction'

    id = Column(CHAR(32), primary_key=True)
    type = Column(String(50))
    user_id = Column(CHAR(32), nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    date_time = Column(DateTime(), default='')
    currency = Column(CHAR(3))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'transaction'
    }

    def __init__(self, id, user_id, amount, currency, date_time=None):
        #TODO gerer les collisions (on fait un truc global?)
        self.id = id
        #TODO Controle des users
        self.user_id = user_id
        self.amount = amount
        if date_time is None:
            date_time = datetime.utcnow()
        self.date_time = date_time
        self.currency = currency

    def __repr__(self):
        return '<Transaction {}>'.format(self.id)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'amount': self.amount,
            'date_time': self.date_time,
            'currency': self.currency,
            'id': self.id,
            'transaction_type': self.type
        }

    def get_fields(self):
        """
        Returns the flask restful type of field.
        """
        return fields.transaction_fields


class Printing(Transaction):
    """
    Records the printings of the users.
    """
    __tablename__ = 'printing'
    __mapper_args__ = {
        'polymorphic_identity': 'printing'
    }

    id = Column(CHAR(32), ForeignKey('transaction.id'), primary_key=True)
    pages_color = Column(Integer)
    pages_grey_level = Column(Integer)
    copies = Column(Integer)

    def __init__(self, id, user, amount, currency, pages_color, pages_grey_level, copies, date_time=None):
        self.amount = amount
        self.pages_color = pages_color
        self.pages_grey_level = pages_grey_level
        self.copies = copies
        super(Printing, self).__init__(id, user, amount, currency, date_time)

    def to_dict(self):
        d = super(Printing, self).to_dict()
        d.update({
            'pages_color': self.pages_color,
            'pages_grey_level': self.pages_grey_level,
            'copies': self.copies
        })
        return d

    def get_fields(self):
        return fields.printing_fields


class LoadingCreditCard(Transaction):
    """
    Records the loadings operations with the credit card made by the user.
    """
    __tablename__ = 'loading_credit_card'
    __mapper_args__ = {
        'polymorphic_identity': 'loading_credit_card'
    }

    id = Column(CHAR(32), ForeignKey('transaction.id'), primary_key=True)
    # On ne sait pas encore ce qu'on aura comme infos ici.


class HelpDesk(Transaction):
    """
    Records the operations made by the help desk.
    """
    __tablename__ = 'help_desk'
    __mapper_args__ = {
        'polymorphic_identity': 'help_desk'
    }

    id = Column(CHAR(32), ForeignKey('transaction.id'), primary_key=True)
