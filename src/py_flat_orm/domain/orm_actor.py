from typing import Callable, TypeVar

from sqlalchemy.engine import Connection, Engine

# Define a type variable for the return type of the closure
T = TypeVar('T')


class OrmActor:
    @staticmethod
    def read(engine: Engine, fn: Callable[[Connection], T]) -> T:
        try:
            with engine.connect() as conn:
                result = fn(conn)
                return result
        except Exception as ex:
            raise ex

    @staticmethod
    def run_with_tx(engine: Engine, fn: Callable[[Connection], T]) -> T:
        with engine.begin() as conn:
            return fn(conn)
