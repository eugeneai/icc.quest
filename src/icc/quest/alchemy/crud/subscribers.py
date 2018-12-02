import icc.quest.alchemy.crud.events as events
import icc.quest.alchemy.models as models
from icc.quest.views import inst_types, FETCH_SETUP
from pyramid.events import subscriber
from sqlalchemy_utils import (
    EmailType, UUIDType,
    PhoneNumberType,
    PhoneNumber)

from sqlalchemy_utils.types.phone_number import PhoneNumberParseException


def fetch_setup(e):
    global FETCH_SETUP

    ctx = e.context
    s = FETCH_SETUP.get(ctx.relation, None)
    if s is not None:
        ctx.fetch = s
    else:
        fetch = ctx.fetch
        fetch['id'] = 'uuid'
        fields = fetch['fields']
        # filter out all refernces
        fetch['fields'] = [f for f in fields
                           if not f.name.endswith('uuid')]


def to_appstruct(e):
    ctx = e.context
    if ctx.relation == models.Institution:
        models.WIDGET_inst_type_uuid.values = inst_types(ctx)
        appstruct = ctx.appstruct
        phone_str = appstruct['phones']
        try:
            phones = phone_str.split(';')
        except AttributeError:
            phones = []
        n = []
        for phone in phones:
            try:
                pn = PhoneNumber(phone, region=models.REGION)
            except PhoneNumberParseException:
                continue
            if pn.is_valid_number():
                phone = pn.national
                if phone.startswith('8'):
                    phone = '+7'+phone[1:]
                n.append(phone)
        phones = n
        if not phones:
            phones = ['']
        appstruct['phones'] = phones


def to_context(e):
    global INST_TYPES

    ctx = e.context
    if ctx.relation == models.Institution:
        appstruct = ctx.appstruct
        n = []
        for phone in appstruct['phones']:
            try:
                pn = PhoneNumber(phone, region=models.REGION)
            except PhoneNumberParseException:
                continue
            if pn.is_valid_number():
                n.append(pn.e164)
            else:
                print("Not valid:", pn)
        appstruct['phones'] = ';'.join(n)
    elif ctx.relation == models.InstitutionType:
        INST_TYPES = None
