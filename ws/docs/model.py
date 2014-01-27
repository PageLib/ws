# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, CHAR, String, DateTime, ForeignKey, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Document(Base):
    """Class for the stored documents"""
    __tablename__ = 'document'

    id = Column(CHAR(32), primary_key=True)
    user_id = Column(CHAR(32), nullable=False)
    date_time = Column(DateTime(), default='')
