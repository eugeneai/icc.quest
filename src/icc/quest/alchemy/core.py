from isu.webapp.storage.file.interfaces import IFile, IFileStorage
from zope.interface import implementer
from collections import OrderedDict
from zope.component import getUtility
import pyramid.threadlocal
from .interfaces import IDataBaseSession
from .models import File
import transaction
import os.path


@implementer(IFileStorage)
class TestFileStorage(object):
    def __init__(self):
        self._files = []

    def store(self, object):
        file = IFile(object)
        self._files.append(file)

    def files(self, filter=None):
        return self._files


@implementer(IFileStorage)
class AlchemyTableFileStorage(object):
    def __init__(self):
        self.session = None
        self.limit = 200

    def _get_session(self):
        # request = pyramid.threadlocal.get_current_registry()
        if self.session is None:
            raise ValueError('Session is None')
        return self.session

    def set_session(self, value):
        self.session = value

    def store(self, object):
        file = IFile(object)
        sess = self._get_session()
        obj = sess.query(File).filter(File.name == file.name).\
            filter(File.mime_type == file.mime_type).first()
        if obj is None:
            obj = File(name=file.name,
                       mime_type=file.mime_type,
                       prov_uuid=None)
        obj.set_content(file.content)
        sess.add(obj)
        transaction.commit()

    def files(self, filter):
        sess = self._get_session()
        return sess.query(File).limit(self.limit).all()

    def load(self, key, no_raise=False):
        sess = self._get_session()
        file = IFile(sess.query(File).get(key))
        if file is None:
            if no_raise:
                return file
            else:
                raise KeyError('no such key')
        return file


def base_ext(filename):
    b, e = os.path.splitext(filename)
    e = e[1:]
    return b, e


@implementer(IFile)
class FieldStorageToIFileAdapter(object):
    def __init__(self, context):
        self.context = context
        self.set_content(context.file.read())
        self.key = 'unapplicable'

    @property
    def name(self):
        return self.context.filename

    @property
    def mime_type(self):
        return self.context.type

    @property
    def ext(self):
        return base_ext(self.name)[1]

    @property
    def base_name(self):
        return base_ext(self.name)[0]

    def set_content(self, content):
        self.content = content


@implementer(IFile)
class ModelFileToIFileAdapter(object):
    def __init__(self, context):
        self.context = context

    @property
    def name(self):
        return self.context.name

    @property
    def mime_type(self):
        return self.context.mime_type

    @property
    def key(self):
        return self.context.uuid

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
