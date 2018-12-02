#
from .core import *
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base, Institution, InstitutionType, Query, Mailing
from .ps_helper import JSONDecoder, JSONEncoder
import icc.quest.alchemy.schema as schema
from pprint import pprint


def includeme(global_config, **settings):
    engine = engine_from_config(global_config.registry.settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    global_config.registry.dbsession = DBSession

    global_config.include('ps_alchemy')

    # add sacrud and project models
    global_config.include('pyramid_sacrud')
    global_config.add_static_view('deform', 'deform:static')

    settings = global_config.registry.settings
    settings['pyramid_sacrud.models'] = (('Institutions',
                                          [Institution, InstitutionType]),
                                         ('Query & mailing', [Query, Mailing]))

    # Now we can add our JSON Decoder and Encoder
    base_resource = settings['ps_alchemy.base_resource']
    base_resource.add_to_registry('json_encoder', JSONEncoder)
    base_resource.add_to_registry('json_decoder', JSONDecoder)

    # FIXME: Remove in production
    # This forces colander to setup itself
    #sess = DBSession()
    # sess.query(InstitutionType).first()
    # pprint("BASE: {}".format(Base.metadata.tables))
    # pprint("Metadata: {}".format(MetaData().tables)) # Contains nothing
