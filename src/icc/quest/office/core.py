# from .interfaces import


class OnlyOfficeContext(object):
    def __init__(self, key, route):
        self.key = key
        self.route = route

    def callback_url(self, request):
        return request.route_url(self.route)
