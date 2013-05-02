import json

from functools import wraps

from foo.web.environment import httpexceptions, Response
from foo.lib.exceptions import APIControllerError, LoginRequired
from foo.model.meta import SchemaEncoder


API_METHOD_MAP = {}

def expose_api(name, check_csrf=True, check_referer=True):
    """ Decorator helper for registering an API method. """
    def decorator(fn):
        API_METHOD_MAP[name] = fn
        fn.exposed_name = name
        fn.check_csrf = check_csrf
        fn.check_referer = check_referer
        return fn
    return decorator


def handle_api(fn):
    """ Decorator helper for handling exposed API methods in views. """
    # TODO: Allow whitelisting API methods?
    @wraps(fn)
    def wrapped(self):
        if 'method' not in self.request.params:
            return fn(self)
        try:
            api_controller(self.request)
        except APIControllerError, e:
            self.request.session.flash(e.message)
        return fn(self)
    return wrapped


def api_controller(request, method_whitelist=None):
    """ Performs the internal exposed API routing and error handling.

    :param request:
        Request object.

    :param method_whitelist:
        If provided, limits the methods which we're allowed to process in this
        call.
    """
    try:
        method = request.params['method']
    except KeyError, e:
        raise APIControllerError("Missing required parameter: %s" % e.args[0])

    if method_whitelist and method not in method_whitelist:
        raise APIControllerError("Method not permitted: %s" % method)

    fn = API_METHOD_MAP.get(method)
    if not fn:
        raise APIControllerError("Method does not exist: %s" % method)

    if fn.check_referer and request.referer:
        expected_referer = request.application_url.split('://', 1)[1]
        request_referer = request.referer.split('://', 1)[1]

        if not request_referer.startswith(expected_referer):
            raise APIControllerError("Bad referer: %s" % request.referer)

    if fn.check_csrf and request.params.get('csrf_token') != request.session.get_csrf_token():
        raise APIControllerError("Invalid csrf_token value: %s" % request.params.get('csrf_token'))

    try:
        return fn(request)
    except KeyError, e:
        raise APIControllerError("Missing required parameter: %s" % e.args[0])


def _report_error(data, e):
    # FIXME: Not a fan of this helper. Need to restructure the code to avoid needing it.
    data['messages'] += [e.message]
    data['code'] = e.code
    data['status'] = 'error'
    return data


def index(request):
    """ The only app-routed view which delegates the rest of the API-related
    functionality. Collates the API result into the final payload and response
    object.
    """
    data = {
        'status': 'ok',
        'code': 200,
        'messages': [],
        'result': {},
    }

    format = request.params.get('format', 'json')
    if format not in ('json', 'redirect', 'fragment'):
        return httpexceptions.HTTPBadRequest('Invalid format requested: %s' % format)

    encode_settings = {'cls': SchemaEncoder}
    if request.params.get('pretty'):
        encode_settings['sort_keys'] = True
        encode_settings['indent'] = 4

    next = request.params.get('next') or request.referer

    try:
        r = api_controller(request)
        if r is not None:
            data['result'] = r

    # FIXME: This isn't the cleanest...
    except APIControllerError, e:
        if format == 'redirect':
            request.session.flash(e.message)
            return httpexceptions.HTTPSeeOther(next or '/')
        _report_error(data, e)

    except LoginRequired, e:
        if format == 'redirect':
            request.session.flash(e.message)
            query = {'next': e.next or next}
            return httpexceptions.HTTPSeeOther(request.route_url('account_login', _query=query))
        _report_error(data, e)

    if format == 'redirect':
        return httpexceptions.HTTPSeeOther(next or '/')
    elif format == 'fragment':
        return data['result']

    body = json.dumps(data, **encode_settings)
    return Response(body, content_type='application/json', status=data['code'])


# Exposed APIs:

@expose_api('ping')
def ping(request):
    return {'ping': 'pong'}
