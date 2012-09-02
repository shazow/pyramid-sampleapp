from foo import model
from foo.model.meta import Session
from foo.lib.exceptions import APIError, LoginRequired


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
    user_id = get_user_id(required=required)
    if not user_id:
        return

    u = Session.query(model.User).get(user_id)
    if not u:
        request.session.pop('user_id', None)
        request.session.save()
        return get_user(required=required) # Try again.

    return u


# API queries

def get(user_id=None, handle=None, email=None):
    if user_id:
        return model.User.get(user_id)

    if handle:
        return model.User.get_by(handle=handle)

    if email:
        return model.User.get_by(email=email)


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
