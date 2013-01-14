from flask import abort, Flask, jsonify, Response, request
from flask.ext.login import login_required
from flask.views import MethodView
from flask_test import TestCase


class BasicTestCase(TestCase):
    def create_app(self):
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


class TagAPI(MethodView):
    tags = {1: {}}
    tag_counter = 1

    def fetch_tag(self, tag_id):
        try:
            return self.tags[tag_id]
        except KeyError:
            abort(404)

    def get(self, tag_id=None):
        if tag_id is not None:
            return jsonify(data=self.fetch_tag(tag_id))
        else:
            return jsonify(data=[tag for tag in self.tags.items()])

    def post(self):
        tag = self.tags[self.tag_counter] = {}
        tag.update(request.form)
        tag['id'] = self.tag_counter
        response = jsonify(data=tag)
        response.status_code = 201
        self.tag_counter += 1
        return response

    @login_required
    def delete(self, tag_id):
        self.fetch_tag(tag_id)
        del self.tags[tag_id]
        return Response(status=204)

    def put(self, tag_id):
        return jsonify(data=self.fetch_tag(tag_id))
