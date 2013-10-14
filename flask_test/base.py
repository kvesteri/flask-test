from contextlib import contextmanager

from flask import json, url_for
from flask.ext.login import user_unauthorized
from flexmock import flexmock

from werkzeug import cached_property
from .view import ViewSetup
from .database import DatabaseSetup


class ContextVariableDoesNotExist(Exception):
    pass


class ApplicationSetup(object):
    def setup(self, obj, app, *args, **kwargs):
        obj.app = app
        obj.app.response_class = _make_test_response(obj.app.response_class)
        obj._app_context = obj.app.app_context()
        obj._app_context.push()

    def teardown(self, obj):
        obj._app_context.pop()
        obj._app_context = None
        obj.app = None


class TestCase(object):
    """
    Base TestCase, all your Flask test cases should inherit this class
    """
    teardown_delete_data = True
    template = None
    view = None
    url = None
    setup_level = 'method'
    setup_delegators = [ApplicationSetup(), ViewSetup(), DatabaseSetup()]

    @property
    def db(self):
        return self.app.extensions['sqlalchemy'].db

    @classmethod
    def create_app(self):
        """
        Create your Flask app here
        """
        raise NotImplementedError

    def after_create_app(self):
        pass

    @classmethod
    def before_class_setup(cls):
        """Simple template method that is invoked before setup_class is
        called."""
        pass

    @classmethod
    def after_class_setup(cls):
        """Simple template method that is invoked after setup_class is
        called."""
        pass

    @classmethod
    def before_class_teardown(cls):
        """Simple template method that is invoked before teardown_class is
        called."""
        pass

    @classmethod
    def after_class_teardown(cls):
        """Simple template method that is invoked after teardown_class is
        called."""
        pass

    def before_method_setup(self, method):
        """Simple template method that is invoked before setup_method is
        called."""
        pass

    def after_method_setup(self, method):
        """Simple template method that is invoked after setup_method is
        called."""
        pass

    def before_method_teardown(self, method):
        """Simple template method that is invoked before teardown_method is
        called."""
        pass

    def after_method_teardown(self, method):
        """Simple template method that is invoked after teardown_method is
        called."""
        pass

    @classmethod
    def setup_class(cls):
        """
        Setup this test case when using class level setup
        """
        if cls.setup_level == 'class':
            cls.before_class_setup()
            app = cls.create_app()
            for setup_delegator in cls.setup_delegators:
                setup_delegator.setup(cls, app)
            cls.after_class_setup()

    @classmethod
    def teardown_class(cls):
        """
        Teardown this test case when using class level setup
        """
        if cls.setup_level == 'class':
            cls.before_class_teardown()
            for setup_delegator in reversed(cls.setup_delegators):
                setup_delegator.teardown(cls)
            cls.after_class_teardown()

    def setup_method(self, method):
        """
        Setup this test case when using method level setup
        """
        if self.setup_level == 'method':
            self.before_method_setup(method)
            app = self.create_app()
            for setup_delegator in self.setup_delegators:
                setup_delegator.setup(self, app)
            self.after_method_setup(method)

    def teardown_method(self, method):
        """
        Teardown this test case when using method level setup
        """
        if self.setup_level == 'method':
            self.before_method_teardown(method)
            for setup_delegator in reversed(self.setup_delegators):
                setup_delegator.teardown(self)
            self.after_method_teardown(method)

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

    def requires_login(self):
        return requires_login()

    def get_page(self):
        return self.client.get(url_for(self.view))

    def _add_template(self, app, template, context):
        self.templates.append((template, context))

    def assert_template_used(self, name):
        """
        Checks if a given template is used in the request.

        :param name: template name
        """
        for template, context in self.templates:
            if template.name == name:
                return True
        raise AssertionError("template %s not used" % name)

    def get_context_variable(self, name):
        """
        Returns a variable from the context passed to the template.

        Raises a ContextVariableDoesNotExist exception if does
        not exist in context.

        :param name: name of variable
        """
        for template, context in self.templates:
            if name in context:
                return context[name]
        raise ContextVariableDoesNotExist

    def assert_context(self, name, value):
        """
        Checks if given name exists in the template context and equals the
        given value.

        :param name: name of context variable
        :param value: value to check against
        """

        try:
            assert self.get_context_variable(name) == value
        except ContextVariableDoesNotExist:
            self.fail("Context variable does not exist: %s" % name)

    def assert_redirects(self, response, location):
        """
        Checks if response is an HTTP redirect to the given location.

        :param response: Flask response
        :param location: relative URL (i.e. without **http://localhost**)
        """
        assert response.status_code in (301, 302)
        assert response.location == "http://localhost" + location

    def assert_status(self, response, status_code):
        """
        Helper method to check matching response status.

        :param response: Flask response
        :param status_code: response status code (e.g. 200)
        """
        assert response.status_code == status_code

    def assert200(self, response):
        """
        Checks if response status code is 200

        :param response: Flask response
        """
        self.assert_status(response, 200)

    def assert201(self, response):
        """
        Checks if response status code is 201

        :param response: Flask response
        """
        self.assert_status(response, 201)

    def assert204(self, response):
        """
        Checks if response status code is 204

        :param response: Flask response
        """
        self.assert_status(response, 204)

    def assert400(self, response):
        """
        Checks if response status code is 400

        :param response: Flask response
        """
        self.assert_status(response, 400)

    def assert401(self, response):
        """
        Checks if response status code is 401

        :param response: Flask response
        """
        self.assert_status(response, 401)

    def assert403(self, response):
        """
        Checks if response status code is 403

        :param response: Flask response
        """

        self.assert_status(response, 403)

    def assert404(self, response):
        """
        Checks if response status code is 404

        :param response: Flask response
        """
        self.assert_status(response, 404)

    def assert405(self, response):
        """
        Checks if response status code is 405

        :param response: Flask response
        """
        self.assert_status(response, 405)

    def assert_flash_message(self, expected_category, expected_message):
        """
        Checks that given flash message was added in given category

        :param expected_category: Flash message category string
        :param expected_message: message that should have been added to the
            flash messages stack
        """
        with self.client.session_transaction() as session:
            messages = session['_flashes']
            assert len(messages) == 1
            category, message = messages[0]
            assert category == expected_category
            assert message == expected_message


class JsonResponseMixin(object):
    """
    Mixin with testing helper methods
    """
    @cached_property
    def json(self):
        return json.loads(self.data)


def _make_test_response(response_class):
    """
    Extends the normal app response by patching the response class to
    include a `json` attribute for quickly getting the response body as
    parsed as JSON.
    """
    class TestResponse(response_class, JsonResponseMixin):
        pass

    return TestResponse


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


@contextmanager
def validates_form(form):
    flexmock(form).should_receive('validate').once()
    yield
