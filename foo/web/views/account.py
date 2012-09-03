from foo import api
from .api import _controller as api_controller
from foo.lib.exceptions import APIControllerError

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response


def create(request):
    redirect_to = request.params.get('next') or '/'
    user_id = api.account.get_user_id(request)
    if user_id:
        return HTTPFound(location=redirect_to)

    context = {'next': redirect_to, 'request': request}
    method = request.params.get('method')
    if not method:
        # Default behaviour, no form submitted.
        return render_to_response('account/create.mako', context , request)

    try:
        # Form submitted, delegate the request to the API controller.
        r = api_controller(request)
    except APIControllerError, e:
        # API Controller rejected the request, re-render the form with the error.
        request.session.flash(e.message)
        context.update(request.params)
        return render_to_response('account/create.mako', context, request)

    # Submission processed successfully, redirect to the next page.
    request.session.flash('Welcome.')
    return HTTPFound(location=redirect_to)
