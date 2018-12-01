
from importlib import import_module


class Config(object):
    """Config setup for CRUD

    """

    def __init__(self, module=None):
        self.module = module

    def is_valid(self):
        return self.module is not None

    def set_model(self, module):
        if typ(model) == str:
            module = import_module(module)
        self.module = module


def set_crud_model_source(config, module):
    config.registry.crud_model_source_config.module = module


def includeme(global_config, **settings):
    global_config.load_zcml("configure.zcml")
    global_config.add_directive('set_crud_model_source',
                                set_crud_model_source)
    global_config.registry.crud_model_source_config = Config()
    # User also should supply reference to models
