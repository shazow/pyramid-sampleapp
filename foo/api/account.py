from foo import model
from foo.model.meta import Session
from foo.lib.exceptions import APIError, LoginRequired

from unstdlib import get_many


# Request helpers

def get_user_id(request, required=False):
    """
    Get the current logged in user_id, else None.

    If required==True, then redirect to login page while preserving the current destination.
    """
    user_id = request.session.get('user_id')
    if user_id:
        return user_id

    if not required:
        return

    raise LoginRequired(next=request.path_qs)


def get_user(request, required=False):
    """
    Get the current logged in User object, else None.
    """
    user_id = get_user_id(request, required=required)
    if not user_id:
        return

    u = model.User.get(user_id)
    if not u:
        request.session.pop('user_id', None)
        request.session.save()
        return get_user(required=required) # Try again.

    return u


def login_user_id(request, user_id):
    """
    Force current session to be logged in as user_id, regardless of credentials.
    """
    # Success
    request.session['user_id'] = user_id
    request.session.save()


def login_user(request):
    """
    Verify user credentials in the request. If valid, set the user_id in the
    session and return the user object.
    """
    email, password = get_many(request.params, ['email', 'password'])

    u = model.User.get_by(email=email)
    if not u:
        raise APIError('User not found.')

    if not u.compare_password(password):
        raise APIError('Invalid password.')

    # Success
    login_user_id(request, u.id)

    return u


def logout_user(request):
    """
    Delete login information from the current session. Log out any user if
    logged in.
    """
    request.session.pop('user_id', None)
    request.session.save()


# API queries

def create(email, password, handle=None, is_admin=False):
    u = model.User.create(email=email, handle=handle, is_admin=is_admin)
    u.set_password(password)

    Session.commit()

    return u


def email_verify(user_id, email_token):
    u = model.User.get_by(id=user_id, email_token=email_token)

    if not u:
        raise APIError('Invalid user: %s' % user_id)

    u.email_token = None
    Session.commit()

    return u
