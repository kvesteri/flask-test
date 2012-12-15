from flask import json
from werkzeug import cached_property


class ApplicationSetup(object):
    @classmethod
    def setup(cls, obj, app, *args, **kwargs):
        obj.app = app
        obj.app.response_class = _make_test_response(obj.app.response_class)
        obj._app_context = obj.app.app_context()
        obj._app_context.push()

    @classmethod
    def teardown(cls, obj):
        obj._app_context.pop()
        obj.app = None


class BaseTestCase(object):
    setup_level = 'method'

    setup_delegator = ApplicationSetup

    @classmethod
    def create_app(self):
        """
        Create your Flask app here
        """
        raise NotImplementedError

    def after_create_app(self):
        pass

    @classmethod
    def before_setup(self, method=None):
        """Simple template method that is invoked before setup_class or
        setup_method are called."""

    @classmethod
    def after_setup(self, method=None):
        """Simple template method that is invoked after setup_class or
        setup_method are called."""

    @classmethod
    def setup_class(cls):
        if cls.setup_level == 'class':
            cls.before_setup()
            cls.setup_delegator.setup(cls, cls.create_app())
            cls.after_setup()

    @classmethod
    def teardown_class(cls):
        if cls.setup_level == 'class':
            cls.before_teardown()
            cls.setup_delegator.teardown(cls)
            cls.after_teardown()

    def setup_method(self, method):
        if self.setup_level == 'method':
            self.before_setup(method)
            self.setup_delegator.setup(self, self.create_app())
            self.after_setup(method)

    def teardown_method(self, method):
        if self.setup_level == 'method':
            self.before_teardown()
            self.setup_delegator.teardown(self)
            self.after_teardown()


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
