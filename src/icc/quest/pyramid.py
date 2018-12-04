import logging
from zope.component import adapter
from pyramid.httpexceptions import HTTPSeeOther

from isu.webapp.views import View, PanelItem
from glob import glob
from pkg_resources import resource_filename
from icc.mvw.interfaces import IView
import os
import os.path
from lxml import etree
from pkg_resources import resource_filename

from icc.quest import alchemy
import deform
import uuid
from .alchemy.models import *
from pyramid_sacrud import PYRAMID_SACRUD_HOME
import transaction
from pyramid.events import subscriber

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("icc.quest")

logger = logging.getLogger("icc.quest")


DATADIR = os.path.abspath(
    os.path.join(
        resource_filename(
            'icc.quest',
            "../../../"),
        "data/study-plans/plans/")
)


class Resource(object):

    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent

    def __getitem__(self, name):
        if name.startswith("@@"):
            raise KeyError("wrong name")
        return Resource(name, self)

    def __str__(self):
        if self.parent is None:
            return "<root>"
        else:
            return str(self.parent) + "/" + self.name

    @property
    def pathname(self):
        s = self
        p = []
        while s is not None:
            if s.name is not None:
                p.append(s.name)
            s = s.parent
        p.reverse()
        return os.path.join(*p)


def resource_factory(request):
    return Resource()


class ViewBase(View):
    title = _("Statistic acquisition platform")

    @property
    def panel_items(self):
        P = PanelItem
        return [
            P(_('Dashboard'), route='home',
              icon='glyphicon glyphicon-dashboard'),
            # P(_('Institutions'), route='inst-fetch',
            #   icon='glyphicon glyphicon-briefcase'),
            # P(_('Institution Types'), route='inst-type-fetch',
            #   icon='glyphicon glyphicon-pencil'),
            P(_('Tables'), route='crud-default',
              icon='glyphicon glyphicon-briefcase'),
            P(_('SACRUD'), route=PYRAMID_SACRUD_HOME,
              icon='glyphicon glyphicon-oil'),
            P(_('Office'), route='only-office',
              icon='glyphicon glyphicon-pencil')
        ]
