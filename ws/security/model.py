# -*- coding: utf-8 -*-

from sqlalchemy import Column, CHAR, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Session(Base):
    """A webservices session."""
    __tablename__ = 'session'

    id = Column(CHAR(32), primary_key=True)
    user_id = Column(CHAR(32))
    opened = Column(DateTime)
    refreshed = Column(DateTime)
    role = Column(String(255))

    def has_role(self, r):
        return self.role == r
