from flask import Flask, json
from werkzeug import cached_property


class BaseTestCase(object):
    def create_app(self):
        """
        Create your Flask app here, with any configuration you need.
        """
        return Flask('test')

    def after_create_app(self):
        pass

    def setup_method(self, method):
        self.app = self.create_app()
        self.after_create_app(self)
        self.app.response_class = _make_test_response(self.app.response_class)
        self._app_context = self.app.app_context()
        self._app_context.push()

    def teardown_method(self, method):
        self._app_context.pop()
        self.app = None


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
