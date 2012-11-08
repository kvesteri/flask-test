from flask import json, template_rendered, url_for
from wtforms_test import FormTestCase as _FormTestCase
from .base import BaseTestCase


class ContextVariableDoesNotExist(Exception):
    pass


class FormTestCase(BaseTestCase, _FormTestCase):
    pass


class ViewMixin(object):
    template = None
    view = None
    url = None

    def get_page(self):
        return self.client.get(url_for(self.view))

    def setup_view(self):
        self.client = self.app.test_client()
        self.xhr_client = xhr_test_client(self, self.app.test_client())
        self._ctx = self.app.test_request_context()
        self._ctx.push()

        self.templates = []
        template_rendered.connect(self._add_template)

    def teardown_view(self):
        self.client = None
        self.xhr_client = None
        self._ctx.pop()
        self._ctx = None
        template_rendered.disconnect(self._add_template)

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


class ViewTestCase(BaseTestCase, ViewMixin):
    def setup_method(self, method):
        super(ViewTestCase, self).setup_method(method)
        self.setup_view()

    def teardown_method(self, method):
        self.teardown_view()
        super(ViewTestCase, self).teardown_method(method)


def xhr_test_client(test_case, client):
    """Decorates regular test client to make XMLHttpRequests with JSON data."""

    original_open = client.open

    def decorated_open(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        kwargs['content_type'] = 'application/json'
        kwargs['headers'] = [
            ('X-Requested-With', 'XMLHttpRequest'),
        ]
        return original_open(self, *args, **kwargs)

    client.open = decorated_open
    return client


class StaticPageMixin(object):
    def test_url(self):
        assert url_for(self.view) == self.url

    def test_returns_200(self):
        response = self.get_page()
        assert response.status_code == 200

    def test_uses_correct_template(self):
        self.get_page()
        self.assert_template_used(self.template)


class StaticPageTestCase(ViewTestCase, StaticPageMixin):
    pass
