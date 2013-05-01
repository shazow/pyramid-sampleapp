from pyramid.request import Request as _Request


__all__ = ['Request']


def _teardown_session(request):
    "Clear SQLAlchemy in-memory cache between requests."
    from foo.model.meta import Session
    Session.remove()


class Request(_Request):
    DEFAULT_FEATURES = {
        'invite_required': True,
    }

    def __init__(self, *args, **kw):
        _Request.__init__(self, *args, **kw)

        self.features = self.DEFAULT_FEATURES.copy()

        # FIXME: Is there a cleaner place to put this?
        self.add_finished_callback(_teardown_session)
