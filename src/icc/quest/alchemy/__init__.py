#
from .core import *
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base

def includeme(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # config = Configurator(settings=settings,
    #                       root_factory='tutorial.models.Root')
    config.include('pyramid_chameleon')
    return config.make_wsgi_app()
