from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from .base import BaseTestCase, ApplicationSetup


class DatabaseSetup(ApplicationSetup):
    def delete_tables(self, db):
        tables = reversed(db.metadata.sorted_tables)
        for table in tables:
            db.session.execute(table.delete())
        db.session.commit()

    def truncate_tables(self, db):
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

    def teardown(self, obj):
        self.teardown_database(obj)
        super(DatabaseSetup, self).teardown(obj)

    def teardown_database(self, obj):
        if 'sqlalchemy' in obj.app.extensions:
            db = obj.app.extensions['sqlalchemy'].db
            db.session.remove()
            if obj.teardown_delete_data:
                self.delete_tables(db)
            db.session.close_all()
            db.engine.dispose()
            self.clear_sqlalchemy_event_listeners()

    def clear_sqlalchemy_event_listeners(self):
        for key, items in event._registrars.items():
            for item in items:
                item.dispatch._clear()


class DatabaseMixin(object):
    teardown_delete_data = True

    @property
    def db(self):
        return self.app.extensions['sqlalchemy'].db


class DatabaseTestCase(BaseTestCase, DatabaseMixin):
    setup_delegator = DatabaseSetup()
