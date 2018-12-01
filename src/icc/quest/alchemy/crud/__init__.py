
from importlib import import_module
from .views import CRUDView
from .events import *


class _Config(object):
    """_Config setup for CRUD

    """

    def __init__(self, module=None):
        self.set_module(module)

    def is_valid(self):
        return self.module is not None

    def set_module(self, module):
        if type(module) == str:
            module = import_module(module)
        self.module = module


def set_crud_model_source(config, module):
    config.registry.crud_model_source_config.set_module(module)


def includeme(global_config, **settings):
    global_config.load_zcml("configure.zcml")
    global_config.add_directive('set_crud_model_source',
                                set_crud_model_source)
    global_config.registry.crud_model_source_config = _Config()
    # User also should supply reference to models
