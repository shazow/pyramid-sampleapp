import json

from pyramid.response import Response
from unstdlib import get_many

from foo.lib.exceptions import APIError, APIControllerError, LoginRequired
from foo.model.meta import SchemaEncoder
from foo import api
from foo import model


API_METHOD_MAP = {}

def expose_api(name, check_csrf=True, check_referer=True):
    """ Decorator helper for registering an API method. """
    # TODO: Add csrf checking option?
    def decorator(fn):
        API_METHOD_MAP[name] = fn
        fn.check_csrf = check_csrf
        fn.check_referer = check_referer
        return fn
    return decorator


def _controller(request, method_whitelist=None):
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

    fn = API_METHOD_MAP.get(method)
    if not fn:
        raise APIControllerError("Method does not exist: %s" % method)

    if fn.check_referer and request.referer and not request.referer.startswith(request.application_url):
        raise APIControllerError("Bad referer: %s" % request.referer)

    if fn.check_csrf and request.params.get('csrf_token') != request.session.get_csrf_token():
        raise APIControllerError("Invalid csrf_token value: %s" % request.params.get('csrf_token'))

    try:
        return fn(request)
    except KeyError, e:
        raise APIControllerError("Missing required parameter: %s" % e.args[0])


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

    encode_settings = {'cls': SchemaEncoder}
    if request.params.get('pretty'):
        encode_settings['sort_keys'] = True
        encode_settings['indent'] = 4

    try:
        r = _controller(request)
        if r:
            data['result'] = r
    except APIControllerError, e:
        data['messages'] += [e.message]
        data['code'] = e.code
        data['status'] = 'error'

    body = json.dumps(data, **encode_settings)
    return Response(body, content_type='application/json', status=data['code'])


# Exposed APIs:

@expose_api('ping')
def ping(request):
    return {'ping': 'pong'}


@expose_api('account.create')
def account_create(request):
    email, password, password_confirm = get_many(request.params, required=['email', 'password', 'password_confirm'])

    if password != password_confirm:
        raise APIControllerError('Password confirmation does not match.')

    u = model.User.get_by(email=email)
    if u:
        raise LoginRequired('Email address already exists. Try logging in?')

    return {'user': api.account.create(email=email, password=password)}


@expose_api('account.login')
def account_login(request):
    try:
        u = api.account.login_user(request)
    except APIError:
        raise APIControllerError('Invalid login.')

    return {'user': u}
