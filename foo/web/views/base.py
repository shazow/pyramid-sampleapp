from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response


class Context(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Controller(object):
    """
    This base class can be used in two ways:

    1. You can use it as a handler base class as defined in pyramid_handlers.

    2. You can use it as a singular route handler if you provide a __call__
    definition with the route logic which returns a response.
    """
    DEFAULT_NEXT = '/'

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.context = Context()

        # Prevent cross-site forwards (possible exploit vector).
        self.next = request.params.get('next')
        if not self.next or self.next.startswith('//') or '://' in self.next:  # Can we do this better?
            self.next = self.DEFAULT_NEXT

    def _default_render_values(self):
        return {
            'c': self.context,
            'request': self.request,
            'session': self.session,
            'is_logged_in': 'user_id' in self.session,
            'current_url': self.request.path_qs,
            'previous_url': self.request.referer,
            'next': self.next,
        }

    def _render(self, renderer_name, extra_values=None, package=None):
        values = self._default_render_values()
        if extra_values:
            values.update(extra_values)

        return render_to_response(renderer_name, value=values, package=package)

    def _redirect(self, *args, **kw):
        "Shortcut for returning pyramid.exceptions.HTTPFound"
        return HTTPFound(*args, **kw)


    def _respond(self):
        "Override this to implement the view's response behavior."
        raise NotImplemented('View response not implemented: %s' % self.__class__.__name__)
