from pytest import raises

from flask import Flask
from flask_test import DatabaseTestCase
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError


class DatabaseSetupTestCase(DatabaseTestCase):
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


class TestDatabaseSetup(DatabaseSetupTestCase):
    def test_setup_creates_tables(self):
        model = self.Model()
        self.db.session.add(model)
        self.db.session.commit()
        assert model.id


class TestDatabaseSetupWithoutTableSetup(DatabaseSetupTestCase):
    setup_tables = False

    def test_setup_does_not_create_tables(self):
        model = self.Model()
        self.db.session.add(model)
        with raises(OperationalError):
            self.db.session.commit()
