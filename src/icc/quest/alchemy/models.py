# SQL Alchemy subsystem
from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class InstitutionType(Base):
    __tablename__ = 'InstitutionType'
    uid=Column(BigInteger, primary_key=True)
    title=Column(String(length=10), unique=True)

class Institution(Base):
    __tablename__ = 'Institution'
    uid=Column(BigInteger, primary_key=True)
    title=Column(String(200), unique=True)
    short_title=Column(String(length=50), unique=True)
    tin=Column(BigInteger, unique=True) # ИНН
    account_details=Column(Text, unique=False)
    address=Column(Text, unique=False)
    head_name=Column(String(length=50), unique=False)
    inst_type = relationship("InstitutionType",
                        back_populates="institutions")
    
# class Root(object):
#     __acl__ = [(Allow, Everyone, 'view'),
#                (Allow, 'group:editors', 'edit')]

#     def __init__(self, request):
#         pass
