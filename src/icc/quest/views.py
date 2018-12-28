import logging
import os
import os.path

from lxml import etree
from pkg_resources import resource_filename
from pyramid.response import FileResponse
from zope.i18nmessageid import MessageFactory

import icc.quest.alchemy.models as models
from .alchemy.crud import Attr
from .alchemy.crud.views import CRUDView
from .pyramid import ViewBase, PanelItemsMixin
import isu.webapp.storage.file as file_mod

logger = logging.getLogger("icc.quest")

_ = MessageFactory("icc.quest")


class DatabaseView(CRUDView):
    pass


class ApplicationView(ViewBase):
    title = _("Statistic acquisition platform DASHBOARD")

    def home(self):
        return self.response()

    @property
    def body(self):
        return "<h1>Hello!</h1>"


class TestView(ViewBase):
    title = 'Test page'

    def test_form(self):

        self.content = open(resource_filename(
            'icc.quest', '../../../input/query1-form.html')).read()

        self.tree = etree.fromstring(self.content)

        self.message = _("Successfully loaded")
        div = etree.Element('div')
        body = self.tree.xpath("//body")[0]
        for child in body:
            div.append(child)
        self.content = etree.tostring(div, pretty_print=True, encoding=str)
        return self.response()


class DummyStorage:
    def __init__(self, root):
        self.root = root

    def path(self, filename):
        return os.path.join(self.root, filename)


class PageView(ViewBase):

    def __init__(self, context, request):
        super(PageView, self).__init__(context=context,
                                       request=request)
        self.message = ""
        self.result = "OK"
        self.exception = ""
        self.level = "success"
        self.content = ""

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
        return DummyStorage(os.path.abspath(resource_filename('icc.quest', '../../../input')))

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


class FileStorageView(file_mod.views.FileStorageView, PanelItemsMixin):
    pass


def on_file_upload(e):
    print("File-upload-event {}".format(e.file))


INST_TYPES = None


def inst_types(ctx):
    global INST_TYPES
    if INST_TYPES is None:
        session = ctx.session
        types = session.query(models.InstitutionType).limit(20).all()
        INST_TYPES = [(o.uuid, o.abbreviation) for o in types]
    return INST_TYPES


FETCH_SETUP = {
    models.InstitutionType: {
        'id': 'uuid',
        'title': _("Institution types"),
        'fields': [
            Attr(name='abbreviation', title=_('Abbreviation')),
            Attr(name='title', title=_('Title'))]},
    models.Institution: {
        'id': 'uuid',
        'title': _("Institutions"),
        'fields': [
            Attr(name='short_title', title=_('Short title')),
            Attr(name='query_email', title=_('Query email')),
            Attr(name='head_name', title=_('Head name')),
            Attr(name='phones', title=_('Phones'))]}
}
