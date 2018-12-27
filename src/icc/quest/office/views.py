from icc.quest.views import ViewBase
from .core import OnlyOfficeContext
from uuid import UUID
from pyramid.response import Response
from isu.webapp.storage.file.interfaces import IFileStorage, IFile
import os.path


class OnlyOfficeView(ViewBase):

    def app(self):
        key = self.request.matchdict['uuid']
        key = UUID(key)
        oocontext = OnlyOfficeContext(key=key.hex)
        oocontext.doc = self.get_document(key)
        return self.response(context=oocontext)

    def load(self):
        name = self.request.matchdict['name']
        key, ext = os.path.splitext(name)
        key = UUID(key)
        doc = self.get_document(key)
        return Response(
            doc.content,
            doc.mime_type)

    def api_call(self):
        print(self.request.POST)
        return self.response(error=0)

    def get_document(self, key):
        storage = self.registry.getUtility(IFileStorage, 'file-storage')
        storage.set_session(self.registry.dbsession())
        return storage.load(key)
