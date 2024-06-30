import logging

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
        MyApp.run_without_tx()
        # MyApp.run_with_tx()

    @staticmethod
    def run_without_tx():
        def run(conn):
            logger.info('run')
            id_gen = IdGen.create()
            people1 = OrmRead.list_all(conn, MyPerson)
            # people2 = MyPerson.list_by_name_starts_with(conn, 'An')
            person = OrmRead.get_by_id(conn, MyPerson, 1)
            logger.info(OrmRead.count(conn, MyPerson))
            logger.info(', '.join([p.name for p in people1]))
            # logger.info(', '.join([p.name for p in people2]))
            logger.info(person.name if person else None)
            p = MyPerson(id=id_gen.get_int(), name='Andrew')
            collector = OrmWrite.validate_and_save(conn, p)
            logger.info(p.id)
            logger.info(collector.has_errors())
            logger.info(OrmRead.count(conn, MyPerson))
            is_deleted = OrmWrite.delete(conn, p)
            logger.info(is_deleted)
            logger.info(OrmRead.count(conn, MyPerson))

        OrmActor.run(RepoDb.get_conn(), run)

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


if __name__ == '__main__':
    MyApp.main()
