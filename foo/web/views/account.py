from unstdlib import get_many

from foo import api
from foo.lib.exceptions import APIError, APIControllerError
from foo.web.environment import httpexceptions

from .api import expose_api, handle_api
from .base import Controller


@expose_api('account.create')
def account_create(request):
    if request.features.get('invite_required'):
        raise APIControllerError("Method not permitted: %s" % account_create.exposed_name)

    email, password, password_confirm, autologin = get_many(request.params, required=['email'], optional=['password', 'password_confirm', 'autologin'])

    if password != password_confirm:
        raise APIControllerError('Password confirmation does not match.')

    if password and len(password) < 3:
        raise APIControllerError('Please choose a longer password.')

    user = api.account.create(email=email, password=password)
    if autologin:
        api.account.login_user_id(request, user.id)

    return {'user': user}


@expose_api('account.login')
def account_login(request):
    try:
        u = api.account.login_user(request)
    except APIError:
        raise APIControllerError('Invalid login.')

    return {'user': u}


class AccountController(Controller):

    @handle_api # Handle api requests posted to this view (such as account.create in this case)
    def create(self):
        if self.request.features.get('invite_required'):
            raise httpexceptions.HTTPNotFound()

        self.title = 'Create an account'

        user_id = api.account.get_user_id(self.request)
        if user_id:
            return self._redirect(location=self.next)

        return self._render('account/create.mako')

    @handle_api
    def login(self):
        self.title = 'Sign in'

        user_id = api.account.get_user_id(self.request)
        if user_id:
            return self._redirect(location=self.next)

        return self._render('account/login.mako')
