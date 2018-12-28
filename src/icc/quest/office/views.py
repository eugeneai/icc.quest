from icc.quest.views import ViewBase
from .core import OnlyOfficeContext
from uuid import UUID
from pyramid.response import Response
from isu.webapp.storage.file.interfaces import IFileStorage, IFile
import os.path
import requests
import transaction
from uuid import uuid1 as _uuid


class OnlyOfficeView(ViewBase):

    def _match(self, name):
        key, ext = os.path.splitext(name)
        key = UUID(key)
        return key, ext

    def app(self):
        name = self.request.matchdict['name']
        file_key, ext = self._match(name)
        key = _uuid()
        oocontext = OnlyOfficeContext(key=key.hex)
        oocontext.document = self.get_document(key=file_key)
        return self.response(oocontext=oocontext)

    def load(self):
        name = self.request.matchdict['name']
        doc = self.get_document(name=name)
        return Response(
            doc.content,
            content_type=doc.mime_type,
            status_code=200)

    def api_call(self):
        filekey = self.request.matchdict['key']
        filekey = UUID(filekey)
        json = self.request.json_body
        ooctxkey = UUID(json['key'])
        print("GOT:", ooctxkey, filekey, json)
        status = json['status']

        if status in [2, 6]:
            url = json["url"]
            rc = requests.get(url)
            storage = self.get_storage()
            content = rc.content
            file = storage.load(filekey)
            file.set_content(content)
            storage.store(file)
            transaction.commit()
        answer = {"error": 0, "key": ooctxkey.hex}
        print("Answer:", answer)
        return answer

    def get_storage(self):
        storage = self.registry.getUtility(IFileStorage, 'file-storage')
        storage.set_session(self.registry.dbsession())
        return storage

    def get_document(self, key=None, name=None):
        if key is not None:
            storage = self.get_storage()
            return storage.load(key)
        else:
            key, ext = self._match(name)
            return self.get_document(key=key)

    def doc_url(self, doc):
        """Returns URL where download document from."""
        file = IFile(doc)
        sname = str(file.key)+'.'+file.ext  # Synthetic name
        return self.request.route_url('only-office-load', name=sname)

    def doc_type(self, doc):
        """Returns type of document in Only Office type context,
        e.g., text ..."""

        file = IFile(doc)
        ext = file.ext
        t = None
        if ext in ["doc", "docm", "docx", "dot",
                   "dotm", "dotx", "epub", "fodt",
                   "htm", "html", "mht", "odt", "ott",
                   "pdf", "rtf", "txt", "djvu", "xps"]:
            t = 'text'
        elif ext in ["csv", "fods", "ods", "ots",
                     "xls", "xlsm", "xlsx", "xlt",
                     "xltm", "xltx"]:
            t = 'spreadsheet'
        elif ext in ["fodp", "odp", "otp", "pot",
                     "potm", "potx", "pps", "ppsm",
                     "ppsx", "ppt", "pptm", "pptx"]:
            t = 'presentation'
        else:
            raise KeyError('unknown file type "{}"'.format(ext))

        print("EXT: {} - {}".format(ext, t))
        return t

    def callback_url(self, key):
        return self.request.route_url('only-office-api', key=key)
