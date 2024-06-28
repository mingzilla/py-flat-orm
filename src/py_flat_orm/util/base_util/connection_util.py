from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool


class ConnectionUtil:

    @staticmethod
    def get_connection(driver_class_name, url, connection_properties):
        # SQLAlchemy uses a connection string that combines the driver, url, and properties
        # Here we are assuming the driver_class_name is a valid SQLAlchemy database URI prefix
        connection_string = f"{driver_class_name}://{url.split(':')[1][2:]}"  # Construct the connection string
        engine = create_engine(connection_string, connect_args=connection_properties, poolclass=NullPool)
        connection = engine.connect()
        return connection

    @staticmethod
    def close(connection: Connection):
        try:
            if connection:
                connection.close()
        except SQLAlchemyError as ignore:
            # Do nothing - don't mind if the close fails
            pass
