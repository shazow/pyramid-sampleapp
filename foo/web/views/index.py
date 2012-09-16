from pyramid.renderers import render_to_response

from foo import api


def index(request):
    u = api.account.get_user(request)
    context = {'hello': u or 'world'}
    return render_to_response('/index.mako', context, request)
