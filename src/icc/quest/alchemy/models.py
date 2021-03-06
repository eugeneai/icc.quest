# SQL Alchemy subsystem
from colanderalchemy import setup_schema
from sqlalchemy.orm import mapper
from sqlalchemy.orm import deferred
from sqlalchemy import event, MetaData
from pyramid.security import Allow, Everyone
from isu.webapp.storage.file.interfaces import IFile
import csv
import re
import mmh3
import uuid
import os.path

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    ForeignKey,
    LargeBinary,
    DateTime
)

from sqlalchemy.dialects.postgresql import ARRAY

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
import colander
import deform
from deform.interfaces import FileUploadTempStore
from uuid import uuid1 as _uuid
from zope.i18nmessageid import MessageFactory
from sacrud import crud_sessionmaker

from zope.interface import implementer
from icc.quest.interfaces import IInstitution

_ = MessageFactory("icc.quest")


# def setup_schema_(mapper, class_):
#     setup_schema(mapper, class_)
#     print("SEUP BASIC:", mapper, class_)


# event.listen(mapper, 'mapper_configured', setup_schema_)

DBSession = crud_sessionmaker(scoped_session(
    sessionmaker(extension=ZopeTransactionExtension())))
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
@implementer(IInstitution)
class InstitutionType(Base):
    __tablename__ = 'institution_types'

    __colanderalchemy_config__ = {'title': _('Type of organizations')}

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                      'title': _('UUID'),
                  }})

    abbreviation = Column(String(length=50), unique=True,
                          info={'colanderalchemy': {
                              'title': _('Abbreviation')
                          }}
                          )

    title = Column(String(length=255), unique=True,
                   info={'colanderalchemy': {
                       # 'typ': colander.String(),
                       # 'widget': deform.widget.HiddenWidget(),
                       'title': _('Tile (long)'),
                   }})

    institutions = relationship("Institution", back_populates="inst_type",
                                info={'colanderalchemy': {
                                    'exclude': True}}
                                )


WIDGET_phone = deform.widget.TextInputWidget(
    mask='+7 (999) 999-99-99'
)

phone = colander.SchemaNode(colander.String(),
                            name='phone',
                            title=_('Phone'),
                            widget=WIDGET_phone)

WIDGET_inst_type_uuid = deform.widget.Select2Widget()


@generic_repr
class Institution(Base):
    __tablename__ = 'institutions'

    __colanderalchemy_config__ = {'title': _('Organizations'),
                                  'overrides': {'phones': {
                                      'typ': colander.Sequence(),
                                      'title': _('Phones'),
                                      'children': [
                                          phone
                                      ]
                                  }}
                                  # 'includes':[column]
                                  }

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})
    title = Column(String(256), unique=True,
                   info={'colanderalchemy': {
                       # 'typ': colander.String(),
                       # 'widget': deform.widget.HiddenWidget(),
                       'title': _("Title (long)")
                   }})
    short_title = Column(String(length=256), unique=True,
                         info={'colanderalchemy': {
                             # 'typ': colander.String(),
                             # 'widget': deform.widget.HiddenWidget(),
                             'title': _("Short title")
                         }})
    tin = Column(BigInteger, unique=True,
                 info={'colanderalchemy': {
                     # 'typ': colander.String(),
                     # 'widget': deform.widget.HiddenWidget(),
                     'title': _("TIN")
                 }})  # ИНН
    rrc = Column(BigInteger, unique=False,
                 info={'colanderalchemy': {
                     # 'typ': colander.String(),
                     # 'widget': deform.widget.HiddenWidget(),
                     'title': _("RRC")
                 }})  # КПП
    account_details = Column(Text, unique=False,
                             info={'colanderalchemy': {
                                 # 'typ': colander.String(),
                                 # 'widget': deform.widget.HiddenWidget(),
                                 'title': _("Account details")
                             }})
    details = Column(Text, unique=False,
                     info={'colanderalchemy': {
                         # 'typ': colander.String(),
                         # 'widget': deform.widget.HiddenWidget(),
                         'title': _("Details")
                     }})
    head_name = Column(String(length=256), unique=False,
                       info={'colanderalchemy': {
                           # 'typ': colander.String(),
                           # 'widget': deform.widget.HiddenWidget(),
                           'title': _("Head name")
                       }})
    head_email = Column(EmailType, unique=True,
                        info={'colanderalchemy': {
                            # 'typ': colander.String(),
                            # 'widget': deform.widget.HiddenWidget(),
                            'title': _("Head email")
                        }})
    query_email = Column(EmailType, unique=True,
                         info={'colanderalchemy': {
                             # 'typ': colander.String(),
                             # 'widget': deform.widget.HiddenWidget(),
                             'title': _("Query email")
                         }})
    phones = Column(String(length=255), unique=False,
                    info={'colanderalchemy': {
                        # 'typ': colander.String(),
                        # 'widget': deform.widget.HiddenWidget(),
                        'title': _("Phones")
                    }})

    inst_type_uuid = Column(UUIDType, ForeignKey('institution_types.uuid'),
                            info={'colanderalchemy': {
                                'typ': colander.String(),
                                'widget': WIDGET_inst_type_uuid,
                                'title': _("Institution type")
                            }})
    inst_type = relationship(InstitutionType, back_populates="institutions",
                             info={'colanderalchemy': {
                                 'exclude': True}})

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
        type_dict = kwargs.get("inst_types", None)
        assert(type_dict is not None)
        del kwargs['inst_types']

        if hasattr(inp, 'write'):
            inp = csv.reader(inp, **kwargs)

        assert(hasattr(inp, "dialect"))

        if dummy:
            return inp

        # Session = kwargs.get("session_maker", None)
        # if Session is None:
        #     raise ValueError('no session_maker parameter supplied')
        # session = Session()

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
            phones = [p.e164 for p in phones]

            det = None
            while True:
                det = details.replace(">>", ">")
                if det == details:
                    details = details.replace(">", " ")
                    break
                details = det
            print(short_title, details, "\n------------")

            short_title = short_title.strip()
            title = title.strip()

            if short_title.startswith('МБДОУ'):
                inst_type = type_dict['mdbou']
            elif short_title.find('СОШ') >= 0:
                inst_type = type_dict['school']
            elif short_title.find('ГИМНАЗИЯ'):
                inst_type = type_dict['gymnasium']
            elif short_title.find('ЛИЦЕЙ'):
                inst_type = type_dict['lycei']
            else:
                raise ValueError('unknown institution type')

            inst = Institution(
                title=title,
                short_title=short_title,
                tin=tin,
                rrc=rrc,
                account_details=account_details,
                details=details,
                head_name=head_name,
                head_email=email,
                query_email=email,
                phones=';'.join(phones),
                inst_type=inst_type
            )

            yield inst


class Query(Base):
    __tablename__ = 'queries'

    __colanderalchemy_config__ = {'title': _('Query'),
                                  # 'overrides':{'phones':{
                                  #     'typ':colander.Sequence(),
                                  #     'title':_('Phones'),
                                  #     'children':[
                                  #         phone
                                  #     ]
                                  # }}
                                  # 'includes':[file_input]
                                  }

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})
    aim = Column(String(256),
                 info={'colanderalchemy': {
                       # 'typ': colander.String(),
                       # 'widget': deform.widget.HiddenWidget(),
                       'title': _("Aim")
                       }})

    description = Column(String(),
                         info={'colanderalchemy': {
                             # 'typ': colander.String(),
                             # 'widget': deform.widget.HiddenWidget(),
                             'title': _("Description")
                         }})

    comment = Column(String(),
                     info={'colanderalchemy': {
                         # 'typ': colander.String(),
                         # 'widget': deform.widget.HiddenWidget(),
                         'title': _("Comment")
                     }})

    form_file_uuid = Column(LargeBinary, unique=False,
                            info={'colanderalchemy': {
                                'typ': deform.FileData(),
                                'widget': deform.widget.HiddenWidget(),
                                'title': _("File of request form"),
                                'ignore': True
                            }})

    table_uuid = Column(String(length=256), unique=False,
                        info={'colanderalchemy': {
                            'widget': deform.widget.HiddenWidget(),
                            'title': _("Table name"),
                            'ignore': True
                        }})

    start = Column(DateTime,
                   info={'colanderalchemy': {
                       # 'typ': colander.String(),
                       # 'widget': deform.widget.HiddenWidget(),
                       'title': _('Starting time')
                   }})

    finish = Column(DateTime,
                    info={'colanderalchemy': {
                        # 'typ': colander.String(),
                        # 'widget': deform.widget.HiddenWidget(),
                        'title': _('Finish time')
                    }})


class Mailing(Base):
    __tablename__ = 'mailing'

    __colanderalchemy_config__ = {'title': _('Mailing'),
                                  # 'overrides': {'phones': {
                                  #     'typ': colander.Sequence(),
                                  #     'title': _('Phones'),
                                  #     'children': [
                                  #         phone
                                  #     ]
                                  # }}
                                  # 'includes':[column]
                                  }

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})

    inst_uuid = Column(UUIDType,
                       info={'colanderalchemy': {
                           'typ': colander.String(),
                           'widget': deform.widget.HiddenWidget(),
                       }})

    query_uuid = Column(UUIDType,
                        info={'colanderalchemy': {
                            'typ': colander.String(),
                            'widget': deform.widget.HiddenWidget(),
                        }})

    data_uuid = Column(UUIDType,
                       info={'colanderalchemy': {
                           'typ': colander.String(),
                           'widget': deform.widget.HiddenWidget(),
                       }})

    sign = Column(DateTime,
                  info={'colanderalchemy': {
                      # 'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                      'title': _('Sign time')
                  }})

    update = Column(DateTime,
                    info={'colanderalchemy': {
                        # 'typ': colander.String(),
                        'widget': deform.widget.HiddenWidget(),
                        'title': _('Update time')
                    }})

    comment = Column(String(256),
                     info={'colanderalchemy': {
                         'widget': deform.widget.TextInputWidget(),
                         'title': _("Comment")
                     }})


@implementer(IFile)
class File(Base):
    """Represents an uploaded file or a derivative from another file, e.g.,
    form freated from an docx template.
    """
    __tablename__ = 'files'

    __colanderalchemy_config__ = {'title': _('File'),
                                  # 'overrides': {'phones': {
                                  #     'typ': colander.Sequence(),
                                  #     'title': _('Phones'),
                                  #     'children': [
                                  #         phone
                                  #     ]
                                  # }}
                                  # 'excludes': ['content']
                                  }

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})

    content = deferred(Column(LargeBinary, unique=False,
                              info={'colanderalchemy': {
                                  'typ': deform.FileData(),
                                  'widget': deform.widget.FileUploadWidget(
                                      tmpstore=FileUploadTempStore()),
                                  'title': _("Content of the file")
                              }}))

    mime_type = Column(String(length=256),
                       info={'colanderalchemy': {
                           'widget': deform.widget.HiddenWidget(),
                           'title': _("Mime type")
                       }})

    name = Column(String(length=256),
                  info={'colanderalchemy': {
                      'title': _("File name")
                  }})

    murmur_hash = Column(UUIDType,  # MurMur3 hash of the content
                         info={'colanderalchemy': {
                             'typ': colander.String(),
                             'widget': deform.widget.HiddenWidget(),
                         }})

    prov_uuid = Column(UUIDType,  # Provenance UUID or NULL
                       info={'colanderalchemy': {
                           'typ': colander.String(),
                           'widget': deform.widget.HiddenWidget(),
                       }})

    def set_content(self, content):
        self.content = content
        self.calc_hash()

    def calc_hash(self):
        self.murmur_hash = uuid.UUID(
            int=mmh3.hash128(self.content, signed=False))

    @property
    def key(self):
        return self.uuid

    @property
    def ext(self):
        return os.path.splitext(self.name)[1][1:]

    @property
    def base_name(self):
        return os.path.splitext(self.name)[0]


class Table(Base):
    """Represents a description of a table used to store
    requested data"""

    __tablename__ = 'tables'

    __colanderalchemy_config__ = {'title': _('Table'),
                                  # 'overrides': {'phones': {
                                  #     'typ': colander.Sequence(),
                                  #     'title': _('Phones'),
                                  #     'children': [
                                  #         phone
                                  #     ]
                                  # }}
                                  # 'includes':[column]
                                  }

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})

    name = Column(String(length=255), unique=True,
                  info={'colanderalchemy': {
                      # 'typ': colander.String(),
                      # 'widget': deform.widget.HiddenWidget(),
                      'title': _('Name of the table in a RDBMS'),
                  }})


# TODO Query Data Tables' first attribute should be uuid,
# the second must be mailing_uuid referencing Mailing.uuid (one-to-many)
# as we suppose, that there are forms requiring adding new rows.


class TestTable(Base):
    __tablename__ = "тесты"

    uuid = Column(UUIDType, primary_key=True, default=_uuid,
                  info={'colanderalchemy': {
                      'typ': colander.String(),
                      'widget': deform.widget.HiddenWidget(),
                  }})

    имя = Column(String(length=255), unique=True,
                  info={'colanderalchemy': {
                      # 'typ': colander.String(),
                      # 'widget': deform.widget.HiddenWidget(),
                      'title': _('Name of the table in a RDBMS'),
                  }})
    
