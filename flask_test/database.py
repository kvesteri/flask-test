from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from .base import BaseTestCase, ApplicationSetup


class DatabaseSetup(ApplicationSetup):
    @classmethod
    def delete_tables(cls, db):
        tables = reversed(db.metadata.sorted_tables)
        for table in tables:
            db.session.execute(table.delete())
        db.session.commit()

    @classmethod
    def truncate_tables(cls, db):
        class TruncateTable(Executable, ClauseElement):
            def __init__(self, *tables):
                self.tables = tables

        @compiles(TruncateTable)
        def visit_truncate_table(element, compiler, **kwargs):
            return "TRUNCATE TABLE %s" % ', '.join(
                compiler.process(table, asfrom=True)
                for table in element.tables
            )

        tables = db.metadata.tables.values()
        db.session.execute(TruncateTable(*tables))
        db.session.commit()

    @classmethod
    def teardown(cls, obj):
        cls.teardown_database(obj)
        ApplicationSetup.teardown(obj)

    @classmethod
    def teardown_database(cls, obj):
        if 'sqlalchemy' in obj.app.extensions:
            db = obj.app.extensions['sqlalchemy'].db
            db.session.remove()
            if obj.teardown_delete_data:
                cls.delete_tables(db)
            db.session.close_all()
            db.engine.dispose()
            cls.clear_sqlalchemy_event_listeners()

    @classmethod
    def clear_sqlalchemy_event_listeners(cls):
        for key, items in event._registrars.items():
            for item in items:
                item.dispatch._clear()


class DatabaseMixin(object):
    teardown_delete_data = True

    @property
    def db(self):
        return self.app.extensions['sqlalchemy'].db


class DatabaseTestCase(BaseTestCase, DatabaseMixin):
    setup_delegator = DatabaseSetup
