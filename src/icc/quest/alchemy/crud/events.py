class Event(object):
    def __init__(self, context):
        self.context = context
        self.action = context.action


class ContextToAppstruct(Event):
    pass


class AppstructToContext(Event):
    pass


class Created(Event):
    pass


class CRUDContextCreated(Created):
    pass


class BeforeFetch(Event):
    pass
