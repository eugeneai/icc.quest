
from importlib import import_module
from .views import CRUDView, Attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from collections import OrderedDict
from sqlalchemy.orm import mapper
from sqlalchemy import event, MetaData
from colanderalchemy import setup_schema
from pyramid.events import ApplicationCreated
from sqlalchemy.orm import configure_mappers


class _Config(object):
    """_Config setup for CRUD

    """

    def __init__(self, module=None, base=None):
        self.set_module(module)
        self.set_base(base)
        self.mappers = OrderedDict()  # Class to Mapper
        self.schemas = {}  # Mapper to colander Schema
        self.relations_ = OrderedDict()

    def is_valid(self):
        return self.module is not None

    def set_module(self, module):
        if type(module) == str:
            module = import_module(module)
        self.module = module
        self.base_ = None

    def set_base(self, base):
        self.base_ = base

    @property
    def metadata(self):
        return self.base.metadata

    @property
    def base(self):
        return getattr(self.module, self.base_)

    @property
    def relations(self):
        return self.relations_
        rs = self.relations_ = OrderedDict()
        base = self.base
        for attr_name in dir(self.module):
            attr = getattr(self.module, attr_name)
            cls = attr.__class__
            if issubclass(cls, DeclarativeMeta):
                if attr_name == self.base_:
                    continue
                rs[attr_name] = cls
        return rs

    def __getitem__(self, relation_name):
        return getattr(self.module, relation_name)

    def invalidate(self):
        self.relations_ = None

    def setup_schema(self, mapper, class_):
        setup_schema(mapper, class_)
        self.relations_[mapper.class_.__name__] = mapper.class_
        self.mappers[mapper.class_] = mapper
        schema = class_.__colanderalchemy__
        self.schemas[mapper] = schema

    def schema(self, cls):
        if hasattr(cls, '__colanderalchemy__'):
            return cls.__colanderalchemy__
        else:
            # It could be mapper.
            return self.schemas[cls]


def set_crud_model_source(config, module, base='Base'):
    config.registry.crud_model_source_config.set_module(module)
    config.registry.crud_model_source_config.set_base(base)


def setup_orm_mapping(event):
    configure_mappers()


def includeme(global_config, **settings):
    global_config.load_zcml("configure.zcml")
    global_config.add_directive('set_crud_model_source',
                                set_crud_model_source)
    config = global_config.registry.crud_model_source_config = _Config()
    # User also should supply reference to models

    event.listen(mapper, 'mapper_configured', config.setup_schema)
