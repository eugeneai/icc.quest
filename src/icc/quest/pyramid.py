from zope.component import adapter
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import FileResponse

from isu.webapp.views import View
from glob import glob
from pkg_resources import resource_filename
from icc.mvw.interfaces import IView
import os
import os.path

from zope.i18nmessageid import MessageFactory
import logging

logger = logging.getLogger("icc.quest")

_ = MessageFactory("icc.quest")

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


class DummyStorage:
    def __init__(self, root):
        self.root = root

    def path(self, filename):
        return os.path.join(self.root, filename)


class PageView(View):

    def __init__(self, context, request):
        super(PageView, self).__init__(context=context,
                                       request=request)
        self.message = ""
        self.result = "OK"
        self.exception = ""
        self.level = "success"
        self.content = ""

    def response(self, **kwargs):
        resp = {
            'view': self,
            'context': self.context
        }
        resp.update(kwargs)
        return resp

    def respjson(self, **kwargs):
        resp = {
            'message': self.message,
            'level': self.level,
            'result': self.result,
            'exception': self.exception,
            'content': self.content
        }
        resp.update(kwargs)
        return resp

    def failed(self, message, exception=None, level='danger'):
        self.message = message
        self.exception = '' if exception is None else str(exception)
        self.level = level
        self.result = "KO"
        return self.response()

    def __call__(self):
        methodnamebase = "route_" + self.name
        methodname = methodnamebase + "_" + self.request.method.lower()
        while True:
            if hasattr(self, methodname):
                method = getattr(self, methodname)
                return method()
            if methodname == methodnamebase:
                break
            methodname = methodnamebase

        raise RuntimeError("Not implemented")

    @property
    def name(self):
        return self.request.view_name

    def pathname(self, split=False, all=False):
        pname = self.context.pathname.strip()
        if all:
            split = True
        if split:
            fn, ext = os.path.splitext(pname)
            if not all:
                return fn, ext
        if all:
            return pname, self.storage.path(pname), fn, ext

        return pname

    @property
    def storage(self):
        # return self.request.storage
        return DummyStorage(
            '/home/eugeneai/projects/code/tech-park/quest/icc.quest/input')

    def main_loader(self):
        filename, physfn, fn, ext = self.pathname(all=True)

        logger.debug('Try to load physical file {}.'.format(physfn))
        logger.info('Request address is {}'.format(self.request.client_addr))

        if ext.lower() in [".html", ".xhtml"]:
            try:
                self.content = open(physfn).read()
                self.message = _("Successfully loaded")
                return self.response()
            except Exception as e:
                return self.failed(
                    _("Cannot load page. It seems it does not exist."),
                    exception=e
                )
        else:
            return FileResponse(physfn)

    def route_content_get(self):
        filename, physfn, fn, ext = self.pathname(all=True)
        return FileResponse(physfn)

    def route_save_post(self):
        filename, physfn, fn, ext = self.pathname(all=True)
        print(filename, physfn, fn, ext)
        self.message = "Fake save"
        body_file = self.request.body_file
        self.storage.save_file(body_file, filename, replace=True)

        return self.respjson()
