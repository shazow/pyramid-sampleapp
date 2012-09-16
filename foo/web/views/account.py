from foo import api
from foo.lib.exceptions import APIControllerError

from .base import Controller
from .api import _controller as api_controller


class AccountController(Controller):

    def create(self):
        user_id = api.account.get_user_id(self.request)
        if user_id:
            return self._redirect(location=self.next)

        method = self.request.params.get('method')
        if not method:
            # Default behaviour, no form submitted.
            return self._render('account/create.mako')

        try:
            # Form submitted, delegate the self.request to the API controller.
            r = api_controller(self.request)
        except APIControllerError, e:
            # API Controller rejected the self.request, re-render the form with the error.
            self.session.flash(e.message)
            return self._render('account/create.mako')

        # Submission processed successfully, login and redirect to the next page.
        api.account.login_user_id(self.request, r['user'].id)
        self.session.flash('Welcome.')

        return self._redirect(location=self.next)


    def login(self):
        user_id = api.account.get_user_id(self.request)
        if user_id:
            return self._redirect(location=self.next)

        method = self.request.params.get('method')
        if not method:
            # Default behaviour, no form submitted.
            return self._render('account/login.mako')

        try:
            # Form submitted, delegate the request to the API controller.
            r = api_controller(self.request)
        except APIControllerError, e:
            # API Controller rejected the request, re-render the form with the error.
            self.session.flash(e.message)
            return self._render('account/login.mako')

        return self._redirect(location=self.next)
