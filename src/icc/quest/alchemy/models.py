# SQL Alchemy subsystem
from pyramid.security import Allow, Everyone
import csv

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
from uuid import uuid1 as _uuid

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


@generic_repr
class InstitutionType(Base):
    __tablename__ = 'institution_types'
    uid = Column(UUIDType, primary_key=True, default=_uuid)
    title = Column(String(length=10), unique=True)


@generic_repr
class Institution(Base):
    __tablename__ = 'institutions'
    uid = Column(UUIDType, primary_key=True, default=_uuid)
    title = Column(String(200), unique=True)
    short_title = Column(String(length=50), unique=True)
    tin = Column(BigInteger, unique=True)  # ИНН
    account_details = Column(Text, unique=False)
    address = Column(Text, unique=False)
    head_name = Column(String(length=50), unique=False)
    head_email = Column(EmailType, unique=True)
    query_email = Column(EmailType, unique=True)

    inst_type_uid = Column(UUIDType, ForeignKey('institution_types.uid'))
    inst_type = relationship(InstitutionType, back_populates="institutions")

    @classmethod
    def default_emails(cls, obj):
        if isinstance(obj, Institution):
            print(obj)
        else:
            raise ValueError('not an Institution instance')

    @classmethod
    def load_from_csv(cls, file_name, **kwargs):
        inp = file_name
        if isinstance(inp, str):
            inp = open(inp)
        dummy = kwargs.setdefault("dummy", False)
        del kwargs["dummy"]
        if hasattr(inp, 'write'):
            inp = csv.reader(inp, **kwargs)

        assert(hasattr(inp, "dialect"))

        if dummy:
            return inp
