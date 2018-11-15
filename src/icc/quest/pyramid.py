import logging
from zope.component import adapter
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.response import FileResponse

from isu.webapp.views import View
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
import transaction

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


class DatabaseView(PageView):
    title = _('Database Editing')

    @property
    def inst_types(self):
        print(self.request.registry.dbsession)
        return {"a": "b"}

    def inst_type_form(self):
        request = self.request
        schema = request.registry.schemas["InstitutionType"]

        get = request.GET
        uuid_ = get.get("id", None)
        buttons = [_('submit')]
        if uuid_ is not None:
            buttons.append(_('delete'))
        form = deform.Form(schema, buttons=buttons)

        appstruct = {'q': 1}
        if uuid_ != None:
            uuid_ = uuid.UUID(uuid_)
            appstruct['uuid'] = uuid_

        if 'submit' in request.POST:
            controls = request.POST.items()
            try:
                appstruct = form.validate(controls)
            except deform.ValidationFailure as e:
                self.form = e.render()
            else:
                try:
                    uuid_ = uuid.UUID(appstruct.get('uuid', None))
                    appstruct['uuid'] = uuid_
                except (TypeError, ValueError):
                    if uuid_ is not None:
                        del appstruct['uuid']

                instType = InstitutionType(**appstruct)
                session = request.registry.dbsession()
                session.add(instType)
                transaction.commit()
                self.form = str(instType)
            return self.response(form=self.form)
        if 'delete' in request.POST:
            self.message = 'OK, Deleted'
            self.form = ''
            return self.response(form=self.form)

        self.form = form.render(appstruct=appstruct)
        return self.response(form=self.form)

    def fetch(self, relation, **kwargs):
        request = self.request
        start = request.GET.get('start', 0)
        length = request.GET.get('length', 200)
        session = request.registry.dbsession()
        result = session.query(relation).offset(start).limit(length).all()
        std = self.response(context=result)
        std.update(kwargs)
        return std

    def fetch_institution_types(self):
        return self.fetch(InstitutionType,
                          id='uuid',
                          title=_("Institution types"),
                          headings=[_('Abbreviation'), _('Title')],
                          fields=['abbreviation', 'title'])

    def fetch_institutions(self):
        return self.fetch(Institution,
                          id='uuid',
                          title=_("Institutions"),
                          headings=[_('Short Title'), _('Head Name'),
                                    _('query_email'), _('phones')],
                          fields=["short_title", "head_name",
                                  "query_email", "phones"]
                          )


class TestView(PageView):
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
