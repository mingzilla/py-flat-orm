from sqlalchemy import create_engine, Engine


class RepoDb:
    @staticmethod
    def get_conn() -> Engine:
        user = "sales"
        password = "salesP1"
        host = "localhost"
        port = "3316"
        database = "storage"

        return RepoDb.create_db_connection(user, password, host, port, database)

    @staticmethod
    def create_db_connection(user, password, host, port, database) -> Engine:
        """Create a SQLAlchemy engine for the database connection."""
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        return engine
