from zope.i18nmessageid import MessageFactory
from icc.quest.pyramid import ViewBase
from pyramid.request import Request
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

import deform
import uuid
import transaction

from collections import namedtuple
import icc.quest.alchemy.crud.events as events
from pprint import pprint

from icc.quest.interfaces import IInstitution

import logging
logger = logging.getLogger("icc.quest")
_ = MessageFactory("icc.quest")


# class CRUDResource(object):
#     def __init__(self, request):
#         self.request = request

#     def __getitem__(self, name):
#         if name.startswith("@@"):
#             raise KeyError("wrong name")
#         return self


class CRUDContext(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        name = self.__class__.__name__
        values = []
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            values.append("{}={}".format(attr,
                                         repr(getattr(self, attr))))

        return "{}({})".format(name, ','.join(values))


RETBTN = \
    _("""<a href='{}' class='btn btn-success'>Back to table</a>""")


class Attr(namedtuple('Heading', ['name', 'title'])):
    pass


class CRUDView(ViewBase):
    """A base class for crud view
    """

    ID = 'id'  # Generic index attribute name

    def __init__(self, *args, **kwargs):
        super(CRUDView, self).__init__(*args, **kwargs)
        self.model = None

        self.crudctx = CRUDContext(action=None)
        if isinstance(self.request, Request):
            self.crudctx.action = self.request.matchdict.get(
                'action', 'default')

    def response(self, **kwargs):
        resp = super(CRUDView, self).response(**kwargs)
        resp['crudctx'] = self.crudctx
        return resp

    @property
    def title(self):
        ctx = self.crudctx
        action = ctx.action
        if action == 'edit':
            return _("Editing relation {}").\
                format(self.crudctx.schema.title)
        elif action == 'browse':
            return self.crudctx.schema.title
        else:
            return _('List of tables')

    def _get_config(self):
        cfg = self.registry.crud_model_source_config
        module_ = cfg.module
        if module_ is None:
            raise ValueError('crud model source is not configured')

        return cfg

    def __call__(self, *args, **kwargs):
        ctx = self.crudctx
        ctx.relation = None
        ctx.rel_name = self.request.matchdict.get('relation', None)
        assert (ctx.rel_name is not None)

        crud_config = self._get_config()

        try:
            ctx.relation = crud_config[ctx.rel_name]
        except AttributeError:
            raise HTTPBadRequest(
                'relation "{}" not found'.format(self.ctx.rel_name))

        # print('CRUD --------')
        # pprint(crud_config.relations)
        schema = ctx.schema = crud_config.schema(ctx.relation)
        ctx.mapper = crud_config.mappers[ctx.relation]
        # print(schema.includes)

        ctx.buttons = [_('submit')]
        get = self.request.GET
        ctx.id = get.get(self.__class__.ID, None)

        if ctx.id is not None:
            ctx.id = uuid.UUID(ctx.id)

        ctx.session = self.registry.dbsession()

        m = None
        try:
            m = getattr(self, ctx.action)
            logger.debug('CRUD Action context {}'.format(ctx))
        except AttributeError as e:
            raise HTTPNotFound(
                'action: "{}" has no handler'.format(ctx.action))

        e = events.CRUDContextCreated(ctx)
        self.registry.notify(e)

        if m is not None:
            return m(*args, **kwargs)

        return self.response()

    @property
    def content(self):
        return "\n<!-- empty content by default -->\n"

    def edit(self):
        retbtn = RETBTN.format(
            self.request.route_path('crud-action',
                                    relation=self.crudctx.rel_name,
                                    action='browse'))

        ctx = self.crudctx
        reg = self.registry

        if ctx.id is not None:
            ctx.buttons.append(_('delete'))

        form = deform.Form(ctx.schema, buttons=ctx.buttons)

        ctx.form = form

        if ctx.id is not None:
            ctx.context = ctx.session\
                             .query(ctx.relation)\
                             .get(ctx.id)
        else:
            ctx.context = ctx.relation()
            e = events.Created(ctx)
            reg.notify(e)

        post = self.request.POST
        if 'submit' in post:
            controls = ctx.controls = post.items()
            try:
                ctx.appstruct = form.validate(controls)
            except deform.ValidationFailure as e:
                content = e.render()
                return self.response(content=content)
            else:
                e = events.AppstructToContext(ctx)
                self.registry.notify(e)
                ctx.context = ctx.schema.\
                    objectify(ctx.appstruct,
                              context=ctx.context)

                ctx.session.add(ctx.context)
                transaction.commit()

                content = "Результат редактирования :{}. <br> {}"\
                    .format(ctx.appstruct, retbtn)

                return self.response(content=content)
        elif 'delete' in post:
            self.message = 'OK, Deleted, Тип того... (на самом деле нет)'
            content = 'Запись удалена. Удачного вам дня. < br/>"\
            " На самом деле нет ' + retbtn
            return self.response(content=content)

        appstruct = ctx.appstruct = ctx.schema.dictify(ctx.context)
        e = events.ContextToAppstruct(ctx)
        reg.notify(e)

        content = form.render(appstruct=appstruct)
        return self.response(content=content)

    class TableView(object):
        def __init__(self, name, relation):
            self.relation = relation
            self.name = name
            self.schema = relation.__colanderalchemy__

        @property
        def table_name(self):
            return self.relation.__tablename__

        @property
        def title(self):
            return self.schema.title

    def default(self):
        cfg = self._get_config()
        metadata = cfg.metadata
        relations = cfg.relations  # Mapping Rel Name -> a DeclarativeMeta
        #tables = metadata.sorted_tables
        self.context = [CRUDView.TableView(name,
                                           rel)
                        for name, rel in relations.items()]
        return self.response(content=self.title)

    def browse(self):
        ctx = self.crudctx
        fetch = ctx.fetch = {}
        rel = ctx.relation

        try:
            ctx.fetch = rel.__crudcontext__['fetch']
        except AttributeError:
            pass
        except KeyError:
            pass

        schema = ctx.schema

        fetch['title'] = schema.title
        rel = ctx.relation
        mapper = ctx.mapper
        fields = []
        for c in mapper.columns:
            name = c.name
            title = schema[name].title
            # check existence in schema
            fields.append(Attr(name=name, title=title))
        fetch['fields'] = fields

        e = events.BeforeFetch(ctx)
        self.registry.notify(e)

        return self.fetch_response(ctx.fetch)

    def fetch_response(self, fields):
        ctx = self.crudctx
        request = self.request
        start = request.GET.get('start', 0)
        length = request.GET.get('length', 200)
        session = ctx.session

        result = session.query(ctx.relation).offset(start).limit(length).all()
        #assert (IInstitution.providedBy(result[0]))
        # print(result[0])
        std = self.response(context=result)
        std.update(fields)
        # print('response data ----------')
        # pprint(std)
        return std
