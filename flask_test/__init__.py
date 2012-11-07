from flask import Flask, json, url_for
from werkzeug import cached_property


class ContextVariableDoesNotExist(Exception):
    pass


class TestCase(object):
    method_teardown_data = True

    def create_app(self):
        """
        Create your Flask app here, with any configuration you need.
        """
        return Flask('test')

    def after_create_app(self, app):
        pass

    def setup_method(self, method):
        self.app = self.create_app()
        self.after_create_app(self.app)
        self.client = self.app.test_client()
        self.xhr_client = xhr_test_client(self, self.app.test_client())
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        self.make_json_aware(self.app)

    def make_json_aware(self, app):
        """
        Extends the normal app by patching the response class to
        include a `json` attribute for quickly getting the response body as
        parsed as JSON.
        """
        self.app.response_class = _make_test_response(self.app.response_class)

    @property
    def db(self):
        return self.app.extensions['sqlalchemy'].db

    def teardown_method(self, method):
        self.teardown_sqlalchemy()
        self._ctx.pop()
        self.app = None
        self.client = None
        self.xhr_client = None
        self._ctx = None

        for key in self.__dict__.keys():
            setattr(self, key, None)

    def teardown_sqlalchemy(self):
        if hasattr(self, 'db'):
            self.db.session.remove()
            if self.method_teardown_data:
                self._delete_table_data()
            self.db.session.close_all()
            self.db.engine.dispose()
            del self.app.extensions['sqlalchemy']
            self._clear_sqlalchemy_event_listeners()

    def _delete_table_data(self):
        """
        Deletes the data in all database tables
        """
        tables = reversed(self.db.metadata.sorted_tables)
        for table in tables:
            self.db.session.execute(table.delete())
        self.db.session.commit()

    def _truncate_tables(self):
        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.sql.expression import Executable, ClauseElement

        class TruncateTable(Executable, ClauseElement):
            def __init__(self, *tables):
                self.tables = tables

        @compiles(TruncateTable)
        def visit_truncate_table(element, compiler, **kwargs):
            return "TRUNCATE TABLE %s" % ', '.join(
                compiler.process(table, asfrom=True)
                for table in element.tables
            )

        tables = self.db.metadata.tables.values()
        self.db.session.execute(TruncateTable(*tables))
        self.db.session.commit()

    def _clear_sqlalchemy_event_listeners(self):
        from sqlalchemy import event
        for key, items in event._registrars.items():
            for item in items:
                item.dispatch._clear()

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
        assert response.status_code == status_code, response.data

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
        Checks if response status code is 201

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


class JsonTestCase(TestCase):
    def setup_method(self, method):
        TestCase.setup_method(self, method)
        self.current = Struct()

    def before_request(self):
        pass

    def put(self, resource=None, data={}, **kwargs):
        if resource is None:
            resource = self.resource
        return self.xhr_client.put(
            url_for(resource, _method='PUT', **kwargs),
            data=data
        )

    def post(self, resource=None, data={}, **kwargs):
        if resource is None:
            resource = self.resource
        response = self.xhr_client.post(
            url_for(resource, _method='POST', **kwargs),
            data=data
        )
        if response.status_code == 201:
            data = response.json['data']
            if isinstance(data, dict):
                setattr(self.current, resource, Struct(data))
            else:
                setattr(self.current, resource, data)
        else:
            setattr(self.current, resource, None)
        return response

    def delete(self, resource=None, **kwargs):
        if resource is None:
            resource = self.resource
        return self.xhr_client.delete(
            url_for(
                resource,
                _method='DELETE',
                **kwargs
            )
        )

    def get(self, resource=None, query_string={}, **kwargs):
        if resource is None:
            resource = self.resource
        return self.xhr_client.get(
            url_for(
                resource,
                _method='GET',
                **kwargs
            )
        )


class CreateTestMixin(object):
    def test_create_returns_201_on_success(self):
        response = self.post()
        self.assert201(response)

    def test_create_returns_created_record_as_json_on_success(self):
        response = self.post()
        assert 'data' in response.json


class IndexTestMixin(object):
    def test_index_returns_200_on_success(self):
        self.post()
        response = self.get()
        self.assert200(response)

    def test_index_returns_list_of_json_objects_on_success(self):
        self.post()
        response = self.get()
        assert len(response.json['data'])


class UpdateTestMixin(object):
    def test_update_returns_200_on_success(self):
        self.post()
        response = self.put()
        self.assert200(response)

    def test_update_returns_404_for_unknown_object(self):
        response = self.put(**{self.identifier: 123123})
        self.assert404(response)

    def test_update_returns_updated_record_as_json_on_success(self):
        self.post()
        response = self.put()
        assert 'data' in response.json


class ShowTestMixin(object):
    def test_show_returns_record_as_json_on_success(self):
        self.post()
        response = self.get()
        assert 'data' in response.json

    def test_show_returns_200_on_success(self):
        self.post()
        response = self.get()
        self.assert200(response)

    def test_show_returns_404_for_unknown_object(self):
        response = self.get(**{self.identifier: 123123})
        self.assert404(response)


class DeleteTestMixin(object):
    def test_delete_returns_204_on_success(self):
        self.post()
        response = self.delete()
        self.assert204(response)

    def test_delete_returns_404_for_unknown_object(self):
        response = self.delete(tag_id=123123)
        self.assert404(response)


class Struct(object):
    '''The recursive class for building and representing objects with.'''
    def __init__(self, obj={}):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, Struct(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, val):
        return self.__dict__[val]

    def __setitem__(self, key, val):
        if isinstance(val, dict):
            self.__dict__[key] = Struct(val)
        else:
            self.__dict__[key] = val

    def __repr__(self):
        return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for
               (k, v) in self.__dict__.iteritems()))


class JsonResponseMixin(object):
    """
    Mixin with testing helper methods
    """
    @cached_property
    def json(self):
        return json.loads(self.data)


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


def _make_test_response(response_class):
    class TestResponse(response_class, JsonResponseMixin):
        pass

    return TestResponse
