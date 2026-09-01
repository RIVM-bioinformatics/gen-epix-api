"""Thread-safe SQLAlchemy engine factory."""

import threading

import sqlalchemy as sa
from sqlalchemy import Engine

# TODO [LSP-3358] make this POOL_RECYCLE configurable via environment variable or configuration file
# Setting should be lower than any Firewall in the network path; recycle
# connections before that to avoid stale-connection errors on pool checkout.
DEFAULT_POOL_RECYCLE = 230


class EngineFactory:
    """Static factory class to create and manage SQLAlchemy engine objs."""

    _LOCK = threading.Lock()
    _ENGINE_MAP: dict[tuple, Engine] = {}

    def __init__(self) -> None:
        """Initialize a EngineFactory instance."""
        raise ValueError(
            "EngineFactory is a static class and should not be instantiated."
        )

    @classmethod
    def create_engine(
        cls,
        connection_string: str,
        echo: bool = False,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
        connect_args: dict | None = None,
    ) -> Engine:
        """
        Create a new SQLAlchemy engine or return an existing one for the given connection string.

        Args:
            connection_string (str): The database connection string.
            echo (bool): If True, the engine will log all statements as well as a repr() of their parameter lists to the default log handler, which defaults to sys.stdout. Defaults to False.
            connect_args (dict | None): Extra keyword arguments forwarded verbatim
                to the underlying DBAPI ``connect()`` call. For pyodbc/mssql use
                ``{"timeout": N}`` to set the login timeout in seconds.

        Returns:
            Engine: The SQLAlchemy engine obj.
        """
        key = cls._compose_key(
            connection_string,
            echo=echo,
            pool_recycle=pool_recycle,
            connect_args=connect_args,
        )
        with cls._LOCK:
            if key not in cls._ENGINE_MAP:
                engine = sa.create_engine(
                    connection_string,
                    echo=echo,
                    pool_recycle=pool_recycle,
                    pool_pre_ping=True,
                    connect_args=connect_args or {},
                )
                cls._ENGINE_MAP[key] = engine
            return cls._ENGINE_MAP[key]

    @classmethod
    def _compose_key(
        cls,
        connection_string: str,
        echo: bool = False,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
        connect_args: dict | None = None,
    ) -> tuple:
        """Compose key."""
        frozen = tuple(sorted(connect_args.items())) if connect_args else ()
        return (connection_string, echo, pool_recycle, frozen)
