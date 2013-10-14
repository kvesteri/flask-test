from flask import json, template_rendered, _request_ctx_stack


class ViewSetup(object):
    def setup(self, obj, app):
        obj.client = app.test_client()
        obj.xhr_client = xhr_test_client(obj, app.test_client())
        obj._ctx = app.test_request_context()
        obj._ctx.push()

        obj.templates = []
        template_rendered.connect(obj._add_template)

    def teardown(self, obj):
        obj.client = None
        obj.xhr_client = None
        if _request_ctx_stack.top and _request_ctx_stack.top.preserved:
            _request_ctx_stack.top.pop()
        obj._ctx.pop()
        obj._ctx = None
        template_rendered.disconnect(obj._add_template)


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
