from contextlib import contextmanager
from flask.ext.login import user_unauthorized

from .view import ViewMixin
from .database import DatabaseMixin
from .base import BaseTestCase, ApplicationSetup


class IntegrationSetup(ApplicationSetup):
    @classmethod
    def setup(cls, obj, app):
        super(IntegrationSetup, cls).setup(obj, app)
        cls.setup_database(obj, app)
        cls.setup_view(obj, app)

    @classmethod
    def teardown(cls, obj):
        cls.teardown_database(obj)
        cls.teardown_view(obj)
        super(IntegrationSetup, cls).teardown(obj)


class IntegrationMixin(DatabaseMixin, ViewMixin):
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
        for client in (self.client, self.xhr_client):
            with client.session_transaction() as s:
                s['user_id'] = user.id
        return user

    def logout(self, user=None):
        for client in (self.client, self.xhr_client):
            with client.session_transaction() as s:
                s['user_id'] = None


class IntegrationTestCase(BaseTestCase, IntegrationMixin):
    setup_delegator = IntegrationSetup


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
