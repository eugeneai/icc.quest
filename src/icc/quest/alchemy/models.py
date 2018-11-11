# SQL Alchemy subsystem
from pyramid.security import Allow, Everyone
import csv
import re

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
from sqlalchemy_utils import (
    EmailType, UUIDType,
    PhoneNumberType,
    PhoneNumber,
    generic_repr
)
from uuid import uuid1 as _uuid

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


RE_EMAIL = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*")
RE_PHONE = re.compile(
    r"((\+7|7|8)?[\s\-]?\(?[0-9]{0,4}\)?[\s\-]?"
    r"[0-9]{0,3}[\s\-]?[0-9]{2,3}[\s\-]?[0-9]{2,3})")

REGION = "RU"


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
    rrc = Column(BigInteger, unique=True)  # КПП
    account_details = Column(Text, unique=False)
    datails = Column(Text, unique=False)
    head_name = Column(String(length=50), unique=False)
    head_email = Column(EmailType, unique=True)
    query_email = Column(EmailType, unique=True)
    tel1 = Column(PhoneNumberType(region=REGION, max_length=12), unique=True)
    tel2 = Column(PhoneNumberType(region=REGION, max_length=12), unique=True)
    mobile = Column(PhoneNumberType(region=REGION, max_length=12), unique=True)

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
        for row in inp:
            title, short_title, tin, rrc, \
                account_details, details, head_name = row
            det_orig = details
            details = details.replace("\n", ">")
            details = details.replace(" ", ">")
            details = details.replace("3952)>", "3952) ")

            dets = details.split("|")
            dets = [d.strip() for d in dets]
            details = "|".join(dets)

            email = RE_EMAIL.search(details)
            if email:
                # details = RE_EMAIL.sub(details, '')
                email = email.group(0)
            phones = RE_PHONE.findall(details)[1:]
            phones = [p[0].strip() for p in phones]
            ps = []
            for phone in phones:
                phone = phone.strip()
                if phone.startswith("-"):
                    continue
                if phone.startswith("7-3952-"):
                    phone = phone.replace("7-3952-", "+7(3952) ")
                if phone.startswith("("):
                    phone = "+7"+phone
                if phone.startswith("8("):
                    phone = phone.replace("8(", "+7(")
                    phone = phone.replace("+7(935", "+7(395")
                if not phone.startswith("+7("):
                    phone = "+7(3952) "+phone
                # phone = phone.replace("-", " ")
                # assert phone.find("395") >= 0
                pn = PhoneNumber(phone, region=REGION)
                # print(pn.e164)
                if pn.is_valid_number():
                    ps.append(pn)

            phones = ps
            tel1 = tel2 = None
            if phones and len(phones) > 1:
                tel1 = phone[0]
                tel2 = phone[1]
            else:
                tel1 = phone[0]
                tel2 = None
            det = None
            while True:
                det = details.replace(">>", ">")
                if det == details:
                    details = details.replace(">", " ")
                    break
                details = det
            print(short_title, details, "\n------------")
