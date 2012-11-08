from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from .base import BaseTestCase


def delete_tables(db):
    tables = reversed(db.metadata.sorted_tables)
    for table in tables:
        db.session.execute(table.delete())
    db.session.commit()


def truncate_tables(db):
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


def teardown_database(db):
    db.session.remove()
    delete_tables(db)
    db.session.close_all()
    db.engine.dispose()
    clear_sqlalchemy_event_listeners()


def clear_sqlalchemy_event_listeners():
    for key, items in event._registrars.items():
        for item in items:
            item.dispatch._clear()


class DatabaseMixin(object):
    @property
    def db(self):
        return self.app.extensions['sqlalchemy'].db

    def setup_database(self):
        pass

    def teardown_database(self):
        teardown_database(self.db)
        del self.app.extensions['sqlalchemy']

    def delete_tables(self):
        delete_tables(self.db)

    def truncate_tables(self):
        truncate_tables(self.db)


class DatabaseTestCase(BaseTestCase, DatabaseMixin):
    def setup_method(self, method):
        super(DatabaseTestCase, self).setup_method(method)
        self.setup_database()

    def teardown_method(self, method):
        self.teardown_database()
        super(DatabaseTestCase, self).teardown_method(method)
