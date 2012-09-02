from foo import model
from foo.model.meta import Session

from datetime import datetime


def _get_all_query(user_id):
    # TODO: Sorting.
    return Session.query(model.List).join(model.UserList).filter(model.UserList.user_id==user_id)


def get_all(user_id):
    return _get_all_query(user_id=user_id)


def create(user_id):
    c = model.List(user_id=user_id)

    Session.commit()

    return c


def _parse_title(body_header):
    # TODO: Make this more robust.
    if not body_header:
        return u'(Untitled)'
    first_line = body_header.split('\n')

    if first_line.startswith('# '):
        return first_line[2:]

    if len(first_line) < 50:
        return first_line

    return u'%s...' % first_line[:47]


def edit(list_id, body_header=None, body_footer=None, order_type=None, is_public=None):
    c = model.List.get(list_id)

    if body_header is not None:
        c.body_head = body_header
        c.title = _parse_title(body_header)

    if body_footer is not None:
        c.body_footer = body_footer

    if order_type is not None:
        c.order_type = order_type
        if order_type != 'manual':
            c.order = ''

    if is_public is not None:
        c.is_public = is_public
        c.time_public = datetime.now()

    Session.commit()

    return c


def add_item(user_id, list_id, body):
    i = model.Item(user_id=user_id, list_id=list_id, body=body)
    i.title = _parse_title(body)

    Session.commit()

    return i
