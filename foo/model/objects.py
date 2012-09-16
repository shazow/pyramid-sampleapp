from .meta import Model
from . import _types

from unstdlib import random_string
from sqlalchemy import orm, types, Index
from sqlalchemy import Column, ForeignKey

from datetime import datetime

import scrypt
import logging


__all__ = ['User']


log = logging.getLogger(__name__)


class User(Model):
    __tablename__ = 'user'
    __json_whitelist__ = ['id', 'email']

    id = Column(types.Integer, primary_key=True)
    time_created = Column(types.DateTime, default=datetime.now, nullable=False)
    time_updated = Column(types.DateTime, onupdate=datetime.now)

    is_admin = Column(types.Boolean, default=False, nullable=False)

    handle = Column(types.String, index=True, unique=True)

    # Email (with a token for verification and recovery)
    email = Column(types.Unicode, nullable=False, index=True, unique=True)
    email_token = Column(types.String(16), default=lambda: random_string(16), nullable=False)

    password_hash = Column(types.LargeBinary, nullable=False)

    PASSWORD_MAXTIME = 0.0001 # Override during environment setup.

    def set_password(self, password, salt_length=64, maxtime=PASSWORD_MAXTIME):
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
        self.password_hash = scrypt.encrypt(random_string(salt_length), password.encode('utf8'), maxtime=maxtime)


    def compare_password(self, password, maxtime=0.5):
        """
        :param password:
            Password input to compare against.

        :param maxtime:
            Must be larger than the time used to encrypt the original password.
        """
        try:
            scrypt.decrypt(self.password_hash, password.encode('utf8'), maxtime=maxtime)
            return True
        except scrypt.error:
            return False
