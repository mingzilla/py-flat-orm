from sqlalchemy import create_engine


class ConnUtil:

    @staticmethod
    def get_conn(user, password, host, port, database):
        """Create a SQLAlchemy engine for the database connection."""
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        return engine


def write_to_db(df, table_name, engine):
    """Write a DataFrame to a specified table in the database."""
    table_name = table_name.lower()  # Ensure the table name is lowercase
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def main():
    # Database connection details
    user = "sales"
    password = "salesP1"
    host = "localhost"
    port = "3316"
    database = "storage"

    sheets_dict = {}

    engine = ConnUtil.get_conn(user, password, host, port, database)

    for table_name, df in sheets_dict.items():
        write_to_db(df, table_name, engine)

    print("Data successfully written to the database.")
