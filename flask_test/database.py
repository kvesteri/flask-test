from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement


class DatabaseSetup(object):
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

    def setup(self, obj, app):
        pass

    def teardown(self, obj):
        if 'sqlalchemy' in obj.app.extensions:
            db = obj.app.extensions['sqlalchemy'].db
            db.session.remove()
            if obj.teardown_delete_data:
                self.delete_tables(db)
            db.session.close_all()
            db.engine.dispose()
