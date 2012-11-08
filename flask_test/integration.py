from contextlib import contextmanager
from flexmock import flexmock

from flask import url_for
from flask.ext.login import user_unauthorized


from .view import ViewMixin
from .database import DatabaseMixin
from .base import BaseTestCase


class IntegrationTestCase(BaseTestCase, DatabaseMixin, ViewMixin):
    def setup_method(self, method):
        super(IntegrationTestCase, self).setup_method(method)
        self.setup_database()
        self.setup_view()

    def teardown_method(self, method):
        self.teardown_database()
        self.teardown_view()
        super(IntegrationTestCase, self).teardown_method(method)

    def create_or_get_user(self):
        """
        Create a user and save it to database.

        :returns: the created user
        """
        pass

    def login(self, user=None):
        """
        Log in the user returned by :meth:`create_user`.

        :returns: the logged in user
        """
        if user is None:
            user = self.create_or_get_user()
        (
            flexmock(user)
            .should_receive('check_password')
            .and_return(True)
        )
        self.client.post(url_for('auth.login'), data=dict(
            email=user.email,
            password=''
        ))
        return user

    def logout(self, user=None):
        self.client.get(url_for('auth.logout'))


@contextmanager
def requires_login():
    user_unauthorized_signals = []

    def _on(sender):
        user_unauthorized_signals.append(sender)

    user_unauthorized.connect(_on)
    try:
        yield
    finally:
        user_unauthorized.disconnect(_on)
        assert user_unauthorized_signals, "The view does not require login."
