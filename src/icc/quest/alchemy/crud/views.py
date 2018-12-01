
from zope.i18nmessageid import MessageFactory
from icc.quest.pyramid import ViewBase

import logging
logger = logging.getLogger("icc.quest")
_ = MessageFactory("icc.quest")


class CRUDResource(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        if name.startswith("@@"):
            raise KeyError("wrong name")
        return self


class CRUDView(ViewBase):
    """A base class for crud view
    """

    def __init__(self, *args, **kwargs):
        super(CRUDView, self).__init__(*args, **kwargs)
        self.model = None

    @property
    def title(self):
        return _("Editing relation {}").format(self.model)

    def __call__(self, *args, **kwargs):
        self.model = 'TABLE'
        print(args)
        print(kwargs)
        return self.response()

    @property
    def content(self):
        return "Content"


def resource_factory(request):
    return CRUDResource(request)
