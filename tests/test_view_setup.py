from flask import Flask
from flask_test import TestCase
from tests import TagAPI


class TestViewSetup(TestCase):
    setup_level = 'class'

    @classmethod
    def create_app(cls):
        app = Flask(__name__)
        app.debug = True
        app.secret_key = 'very secret'

        tag_view = TagAPI.as_view('tag')
        app.add_url_rule('/tags', defaults={'tag_id': None},
                         view_func=tag_view, methods=['GET'])
        app.add_url_rule('/tags', view_func=tag_view, methods=['POST'])
        app.add_url_rule('/tags/<int:tag_id>', view_func=tag_view,
                         methods=['GET', 'PUT', 'DELETE'])

        return app

    def test_initializes_xhr_client(self):
        assert self.xhr_client

    def test_initializes_client(self):
        assert self.client

    def test_wraps_request_objects(self):
        response = self.xhr_client.get('/tags/1')
        response.json  # should have json attribute
