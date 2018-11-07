from __future__ import print_function
__import__('pkg_resources').declare_namespace(__name__)
import logging
import os
from pkg_resources import resource_filename

logger = logging.getLogger("icc.quest")

def includeme(global_config, **settings):
    # from .pyramid import configurator
    configurator(global_config, **settings)


def configurator(config, **settings):

    # storage = config.registry.getUtility(IFileStorage)
    # try:
    #     static_dir = config.registry.settings["storage.static"]
    # except KeyError:
    #     raise RuntimeError("storage.static settings needed")

    # static_dir = os.path.join(storage.base_path, static_dir)
    # static_dir = os.path.abspath(static_dir)

    config.load_zcml("icc.quest:static-assets.zcml")
    static_dir = resource_filename('icc.quest','templates/static')
    for d in os.listdir(static_dir):
        _name = "/APPSD/" + d
        _path = os.path.join(static_dir, d)
        config.add_static_view(name=_name, path=_path)
        logger.debug("Configurator: route='{}' path='{}'".format(
            _name, _path
        ))

    config.load_zcml("icc.quest:configure.zcml")
    # config.add_static_view(path='icc.quest/templates/static', name='/APPSD')
