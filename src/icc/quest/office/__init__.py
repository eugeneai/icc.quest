from pkg_resources import resource_filename
import os
import logging

__import__('pkg_resources').declare_namespace(__name__)

logger = logging.getLogger("icc.quest")


def includeme(global_config, **settings):
    configurator(global_config, **settings)


def configurator(config, **settings):
    config.load_zcml("icc.quest.office:configure.zcml")
