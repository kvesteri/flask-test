from flask import Flask, json
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

    def create_app(self):
        """
        Create your Flask app here, with any configuration you need.
        """
        return Flask('test')

    def after_create_app(self):
        pass

    @classmethod
    def setup_class(cls):
        if cls.setup_level == 'class':
            cls.setup_delegator.setup(cls, cls.create_app())

    @classmethod
    def teardown_class(cls):
        if cls.setup_level == 'class':
            cls.setup_delegator.teardown(cls)

    def setup_method(self, method):
        if self.setup_level == 'method':
            self.setup_delegator.setup(self, self.create_app())

    def teardown_method(self, method):
        if self.setup_level == 'method':
            self.setup_delegator.teardown(self)


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
