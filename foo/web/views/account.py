from foo import api

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response


def _create_account(request):
    # TODO: This should be in an api controller.
    pass


def create(request):
    redirect_to = request.params.get('next')
    user_id = api.account.get_user_id(request)
    if user_id:
        raise HTTPFound(location=redirect_to)

    method = request.params.get('method')
    if not method:
        return render_to_response('account/create.mako', {'next': redirect_to, 'request': request}, request)

    fn = {
        'account.create': _create_account
    }[method]
    return fn(request)
