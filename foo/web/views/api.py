import json

from pyramid.response import Response
from unstdlib import get_many

from foo.lib.exceptions import APIControllerError
from foo.model._types import SchemaEncoder
from foo import api


API_METHOD_MAP = {}

def expose_api(name):
    """ Decorator helper for registering an API method. """
    # TODO: Add csrf checking option?
    def decorator(fn):
        API_METHOD_MAP[name] = fn
        return fn
    return decorator


def _controller(request):
    """ Performs the internal exposed API routing and error handling.
    """
    try:
        method = request.params['method']
    except KeyError, e:
        raise APIControllerError("Missing required parameter: %s" % e.args[0])

    fn = API_METHOD_MAP.get(method)
    if not fn:
        raise APIControllerError("Method does not exist: %s" % method)

    # Simple check for XSS
    if request.referer and not request.referer.startswith(request.application_url):
        raise APIControllerError("Bad referer: %s" % request.referer)

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

@expose_api('account.create')
def account_create(request):
    email, password, password_confirm = get_many(request.params, required=['email', 'password', 'password_confirm'])

    if password != password_confirm:
        raise APIControllerError("Password confirmation doesn't match.")

    api.account.create(email=email, password=password)
