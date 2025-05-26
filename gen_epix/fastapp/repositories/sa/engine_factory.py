import threading

import sqlalchemy as sa
from sqlalchemy import Engine

DEFAULT_POOL_RECYCLE = 1800


class EngineFactory:
    """
    Static factory class to create and manage SQLAlchemy engine objs.
    """

    _LOCK = threading.Lock()
    _ENGINE_MAP: dict[tuple, Engine] = {}

    def __init__(self) -> None:
        raise ValueError(
            "EngineFactory is a static class and should not be instantiated."
        )

    @classmethod
    def create_engine(
        cls,
        connection_string: str,
        echo: bool = False,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
    ) -> Engine:
        """
        Create a new SQLAlchemy engine or return an existing one for the given connection string.

        Args:
            connection_string (str): The database connection string.
            echo (bool): If True, the engine will log all statements as well as a repr() of their parameter lists to the default log handler, which defaults to sys.stdout. Defaults to False.

        Returns:
            Engine: The SQLAlchemy engine obj.
        """
        key = cls._compose_key(connection_string, echo=echo, pool_recycle=pool_recycle)
        with cls._LOCK:
            if key not in cls._ENGINE_MAP:
                engine = sa.create_engine(
                    connection_string, echo=echo, pool_recycle=pool_recycle
                )
                cls._ENGINE_MAP[key] = engine
            return cls._ENGINE_MAP[key]

    @classmethod
    def _compose_key(
        cls,
        connection_string: str,
        echo: bool = False,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
    ) -> tuple[str, bool, int]:
        return (connection_string, echo, pool_recycle)
