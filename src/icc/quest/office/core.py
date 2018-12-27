# from .interfaces import


class OnlyOfficeContext(object):
    def __init__(self, key="default", route="only-office-api"):
        self.key = key
        self.route = route

    def callback_url(self, request):
        return request.route_url(self.route)
