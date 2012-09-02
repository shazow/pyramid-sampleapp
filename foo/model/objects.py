from .meta import Model
from . import _types

from foo.lib.helpers import random_string

from sqlalchemy import orm, types, Index
from sqlalchemy import Column, ForeignKey

from datetime import datetime

import scrypt
import logging


__all__ = ['User', 'List', 'Item']


log = logging.getLogger(__name__)


class User(Model):
    __tablename__ = 'user'

    id = Column(types.Integer, primary_key=True)
    time_created = Column(types.DateTime, default=datetime.now, nullable=False)
    time_updated = Column(types.DateTime, onupdate=datetime.now)

    is_admin = Column(types.Boolean, default=False, nullable=False)

    handle = Column(types.String, nullable=False, index=True, unique=True)

    # Email (with a token for verification and recovery)
    email = Column(types.Unicode, nullable=False, index=True, unique=True)
    email_token = Column(types.String(16), default=lambda: random_string(16), nullable=False)

    password_hash = Column(types.String, nullable=False)


    def set_password(self, password, salt_length=64, maxtime=0.0001):
        """
        :param password:
            Password to set for the user.

        :param salt_length:
            A random string of this length will be generated and encrypted
            using the password.

        :param maxtime:
            Minimum time spent encrypting the password. This is very low by
            default (0.0001 seconds). Pass in a larger value in production
            (preferably configured in the .ini)
        """
        self.password_hash = scrypt.encrypt(random_string(salt_length), password, maxtime=maxtime)


    def compare_password(self, password, maxtime=0.5):
        """
        :param password:
            Password input to compare against.

        :param maxtime:
            Must be larger than the time used to encrypt the original password.
        """
        try:
            scrypt.decrypt(self.password_hash, password, maxtime=maxtime)
            return True
        except scrypt.error:
            return False


class List(Model):
    __tablename__ = 'list'

    id = Column(types.Integer, primary_key=True)
    time_created = Column(types.DateTime, default=datetime.now, nullable=False)
    time_updated = Column(types.DateTime, onupdate=datetime.now)

    user_id = Column(types.Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    user = orm.relationship(User)

    # Was this list forked from another?
    parent_list_id = Column(types.Integer, ForeignKey('list.id', ondelete='SET NULL'))

    # What is the original node of this fork chain?
    root_list_id = Column(types.Integer, ForeignKey('list.id', ondelete='SET NULL'))

    # TODO: num_child_lists
    # TODO: num_users

    title = Column(types.Unicode, nullable=False, default=u'(Untitled)') # Extracted from `body_header`.
    body_header = Column(types.UnicodeText, nullable=False, default=u'')
    body_footer = Column(types.UnicodeText, nullable=False, default=u'')

    order_type = Column(_types.Enum(['manual', 'time_created', 'time_updated', 'title']), nullable=False, default='time_created')
    order = Column(types.LargeBinary, nullable=False, default='') # Comma-separated primary keys.

    is_public = Column(types.Boolean, default=True, nullable=False)
    time_public = Column(types.DateTime)

    users = orm.relationship(User, backref='lists', secondary='user_list')


class UserList(Model):
    __tablename__ = 'user_list'

    id = Column(types.Integer, primary_key=True)
    time_created = Column(types.DateTime, default=datetime.now, nullable=False)
    time_updated = Column(types.DateTime, onupdate=datetime.now)

    shared_by_user_id = Column(types.Integer, ForeignKey(User.id, ondelete='SET NULL'))
    user_id = Column(types.Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    list_id = Column(types.Integer, ForeignKey(List.id, ondelete='CASCADE'), nullable=False)

    can_write = Column(types.Boolean, default=True, nullable=False)

Index('ix_user_source',
      UserList.user_id,
      UserList.list_id,
      unique=True)


class Item(Model):
    __tablename__ = 'item'

    id = Column(types.Integer, primary_key=True)
    time_created = Column(types.DateTime, default=datetime.now, nullable=False)
    time_updated = Column(types.DateTime, onupdate=datetime.now)

    user_id = Column(types.Integer, ForeignKey(User.id, ondelete='CASCADE'))
    list_id = Column(types.Integer, ForeignKey(List.id, ondelete='CASCADE'))

    title = Column(types.Unicode) # Extracted from `body`.
    body = Column(types.UnicodeText)

    is_completed = Column(types.Boolean, default=False, nullable=False)
    time_completed = Column(types.DateTime)
    note_completed = Column(types.UnicodeText)

    # TODO: is_visible?


# TODO: class AuthEmail
# TODO: class {AuthFacebook, AuthTwitter, AuthGoogle}

# TODO: class NotifyQueue
# TODO: class NotifySummary
