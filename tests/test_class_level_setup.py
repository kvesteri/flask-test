from flask import Flask
from flask_test import ViewTestCase
from tests import TagAPI


class TestClassLevelSetup(ViewTestCase):
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

    def test_method1(self):
        assert self.app.secret_key == 'very secret'

    def test_method2(self):
        assert self.app.secret_key == 'very secret'
