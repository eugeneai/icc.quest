from zope.interface import Interface, Attribute


class IDocumentDescription(Interface):
    type = Attribute('Document type, e.g. "text"')
    ext = Attribute('Document extension')
    title = Attribute('Title of the document, optionally with extension')
    url = Attribute('URL of the document')


class IContext(Interface):
    key = Attribute('Key sequence, defining session')

    def callback_url(request):
        """Returns callback url,
        generated using request"""
