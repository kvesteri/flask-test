from flask import Flask
from flask_test import TestCase
from flask.ext.sqlalchemy import SQLAlchemy


class DatabaseSetupTestCase(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.debug = True
        app.secret_key = 'very secret'
        db = SQLAlchemy()
        db.init_app(app)

        class Model(db.Model):
            __tablename__ = 'model'
            id = db.Column(db.Integer, primary_key=True)

        self.Model = Model
        return app
