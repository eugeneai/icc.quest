# SQL Alchemy subsystem
from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    ForeignKey
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
)

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy_utils import EmailType, UUIDType, generic_repr

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


@generic_repr
class InstitutionType(Base):
    __tablename__ = 'institution_type'
    uid = Column(UUIDType, primary_key=True)
    title = Column(String(length=10), unique=True)


@generic_repr
class Institution(Base):
    __tablename__ = 'institution'
    uid = Column(UUIDType, primary_key=True)
    title = Column(String(200), unique=True)
    short_title = Column(String(length=50), unique=True)
    tin = Column(BigInteger, unique=True)  # ИНН
    account_details = Column(Text, unique=False)
    address = Column(Text, unique=False)
    head_name = Column(String(length=50), unique=False)
    head_email = Column(EmailType, unique=True)
    query_email = Column(EmailType, unique=True)

    inst_type_uid = Column(Integer, ForeignKey('institution_type.uid'))
    inst_type = relationship(InstitutionType,
                             back_populates="institutions")

# class Root(object):
#     __acl__ = [(Allow, Everyone, 'view'),
#                (Allow, 'group:editors', 'edit')]

#     def __init__(self, request):
#         pass
