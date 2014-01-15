# -*- coding: utf-8 -*-

import datetime
from sqlalchemy import Column, CHAR, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import config

Base = declarative_base()


class Session(Base):
    """A webservices session."""
    __tablename__ = 'session'

    id = Column(CHAR(32), primary_key=True)  # used as token
    user_id = Column(CHAR(32))
    opened = Column(DateTime)
    refreshed = Column(DateTime)
    role = Column(String(255))

    def has_role(self, r):
        return self.role == r

    @property
    def expires(self):
        return self.refreshed + datetime.timedelta(seconds=config.SESSION_LIFETIME)

    @property
    def isActive(self):
        return self.expires > datetime.now()


class User(Base):
    __tablename__ = 'user'

    id = Column(CHAR(32), primary_key=True)
    login = Column(String(50))
    password_hash = Column(String(40))  # sha1 length
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(String(255))