from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

class ConnectionUtil:

    @staticmethod
    def get_connection(driver: str, url: str, **kwargs) -> Connection:
        try:
            engine = create_engine(f'{driver}://{url}', **kwargs)
            connection = engine.connect()
            return connection
        except SQLAlchemyError as ex:
            raise RuntimeError(f"Error connecting to database: {ex}")

    @staticmethod
    def close(connection: Connection):
        try:
            if connection:
                connection.close()
        except SQLAlchemyError as ignore:
            # Do nothing - don't mind if the close fails
            pass
