from typing import Callable, TypeVar

from sqlalchemy.engine import Connection, Engine

from py_flat_orm.util.base_util.connection_util import ConnectionUtil

# Define a type variable for the return type of the closure
T = TypeVar('T')


class OrmActor:
    @staticmethod
    def run(engine: Engine, fn: Callable[[Connection], T]) -> T:
        try:
            with engine.connect() as conn:
                result = fn(conn)
                return result
        except Exception as ex:
            raise ex

    @staticmethod
    def run_in_tx(fn: Callable[[Connection], T], driver: str, url: str, **kwargs) -> T:
        """
        Executes the provided closure `fn` within a transaction and commits or rolls back based on the result.

        Args:
        - fn (Callable[[Connection], T]): The closure to execute, which takes a Connection as argument and returns a value.
        - driver (str): Database driver (e.g., 'postgresql', 'mysql').
        - url (str): Database URL.
        - kwargs: Additional keyword arguments passed to create_engine.

        Returns:
        - T: Result of executing the closure `fn`.

        Raises:
        - RuntimeError: If there's an error connecting to the database or executing within the transaction.
        """
        connection = None
        try:
            connection = ConnectionUtil.get_connection(driver, url, **kwargs)
            connection.begin()
            result = fn(connection)
            connection.commit()
            return result
        except Exception as ex:
            if connection:
                connection.rollback()
            raise ex
        finally:
            ConnectionUtil.close(connection)

    @staticmethod
    def terminate():
        """
        Raises an exception to terminate the transaction and rollback changes.
        """
        raise Exception('Terminate transaction and rollback')


# Example usage:
if __name__ == "__main__":
    driver = 'postgresql'
    url = 'your_database_url'


    def example_function(connection: Connection) -> None:
        # Example logic inside the closure
        result_proxy = connection.execute("SELECT * FROM your_table")
        for row in result_proxy:
            print(row)


    try:
        # Example of running without a transaction
        OrmActor.run(example_function, driver, url)

        # Example of running within a transaction
        OrmActor.run_in_tx(example_function, driver, url)

    except Exception as ex:
        print(f"Error occurred: {ex}")
