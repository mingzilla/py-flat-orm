import logging

from sqlalchemy import text, Connection

from py_flat_orm.domain.orm_actor import OrmActor
from py_flat_orm.domain.orm_read import OrmRead
from py_flat_orm.domain.orm_write import OrmWrite
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector
from py_flat_orm.util.base_util.id_gen import IdGen
from test_data.integration.my_person import MyPerson
from test_data.integration.repo_db import RepoDb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyApp:
    @staticmethod
    def main():
        # MyApp.run_it()
        OrmActor.run(RepoDb.get_conn(), MyApp.run_without_tx1)

        # MyApp.run_with_tx()

    @staticmethod
    def run_without_tx1(conn: Connection):
        people3 = [OrmRead.get_by_id(conn, MyPerson, 3)]
        logger.info(', '.join([p.name for p in people3]))

    @staticmethod
    def run_without_tx(conn: Connection):
        logger.info('run')
        id_gen = IdGen.create()

        # 1
        people1 = OrmRead.list_all(conn, MyPerson)
        logger.info(', '.join([p.name for p in people1]))

        # 2
        people2 = MyPerson.list_by_name_starts_with(conn, 'An')
        logger.info(', '.join([p.name for p in people2]))

        # 3
        select_statement = f"SELECT * FROM {MyPerson().table_name()} WHERE usercode = :usercode"
        people3 = OrmRead.list(conn, MyPerson, select_statement, {'usercode': "Bob"})
        logger.info(', '.join([p.name for p in people3]))

        # Above is Tested

        person = OrmRead.get_by_id(conn, MyPerson, 1)
        logger.info(OrmRead.count(conn, MyPerson))
        logger.info(person.name if person else None)
        p = MyPerson(id=id_gen.get_int(), name='Andrew')
        collector = OrmWrite.validate_and_save(conn, p)
        logger.info(p.id)
        logger.info(collector.has_errors())
        logger.info(OrmRead.count(conn, MyPerson))
        is_deleted = OrmWrite.delete(conn, p)
        logger.info(is_deleted)
        logger.info(OrmRead.count(conn, MyPerson))

    @staticmethod
    def run_with_tx():
        error_map = {}

        def run_in_tx(conn):
            logger.info('runInTx')
            id_gen = IdGen.create()
            logger.info(OrmRead.count(conn, MyPerson))
            collector1 = OrmWrite.validate_and_save(conn, MyPerson(id=id_gen.get_int(), name='Bobby'))
            logger.info(OrmRead.count(conn, MyPerson))
            p = MyPerson(name='Christine')
            collector2 = OrmWrite.validate_and_save(conn, p)
            logger.info(OrmRead.count(conn, MyPerson))
            people = [collector1, collector2]
            have_errors = OrmErrorCollector.have_errors(people)
            if have_errors:
                error_map['people'] = OrmErrorCollector.to_error_maps(people)
                OrmActor.terminate()

        OrmActor.run_in_tx(RepoDb.get_conn(), run_in_tx)
        logger.info(error_map)

    @staticmethod
    def run_it():
        engine = RepoDb.get_conn()
        with engine.connect() as connection:
            # Define a select statement
            query = text("select * from mis_users")

            # Execute the select statement
            result = connection.execute(query)

            # Fetch all rows from the result
            rows = result.fetchall()

            # Print the rows
            for row in rows:
                print(row)


if __name__ == '__main__':
    MyApp.main()
