#
from .core import *
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base, Institution, InstitutionType
from .ps_helper import JSONDecoder, JSONEncoder
import icc.quest.alchemy.schema as schema


def includeme(global_config, **settings):
    engine = engine_from_config(global_config.registry.settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    global_config.registry.dbsession = DBSession

    global_config.include('ps_alchemy')

    # add sacrud and project models
    global_config.include('pyramid_sacrud')

    settings = global_config.registry.settings
    settings['pyramid_sacrud.models'] = (('Institutions',
                                          [Institution, InstitutionType]),
                                         ('Group2', [Institution]))

    # Now we can add our JSON Decoder and Encoder
    base_resource = settings['ps_alchemy.base_resource']
    base_resource.add_to_registry('json_encoder', JSONEncoder)
    base_resource.add_to_registry('json_decoder', JSONDecoder)
