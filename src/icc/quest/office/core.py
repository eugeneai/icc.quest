# from .interfaces import
from zope.interface import implementer
from isu.webapp.storage.file.interfaces import IFile
import os.path


class OnlyOfficeContext(object):
    def __init__(self, key="default", route="only-office-api"):
        self.key = key
        self.route = route

    def callback_url(self, request):
        return request.route_url(self.route)


def base_ext(filename):
    b, e = os.path.splitext(filename)
    e = e[1:]
    return b, e


@implementer(IFile)
class RequestsResponseToIFileAdapter(object):
    """This is partial implementation of the adapter"""

    def __init__(self, context):
        self.context = context

    @property
    def mime_type(self):
        return self.context.headers['Content-Type']

    @property
    def content(self):
        return self.context.content

    @property
    def ext(self):
        return base_ext(self.name)[1]

    @property
    def base_name(self):
        return base_ext(self.name)[0]

    def set_content(self, content):
        return self.context.set_content(content)
