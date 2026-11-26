"""Thread-safe SQLAlchemy engine factory."""

import os
import threading
from collections.abc import Mapping

import sqlalchemy as sa
from sqlalchemy import Engine

# TODO [LSP-3358] make this POOL_RECYCLE configurable via environment variable or configuration file
# Setting should be lower than any Firewall in the network path; recycle
# connections before that to avoid stale-connection errors on pool checkout.
DEFAULT_POOL_RECYCLE = 230

# Connection pool size per engine (per worker process). Request handlers run in
# FastAPI's threadpool (40 threads by default), so the pool allows as many
# connections; otherwise threads beyond the pool wait up to pool_timeout for a
# connection. Overflow connections are closed again when returned. Mind the
# database's connection/worker limit: replicas x workers x (size + overflow).
DEFAULT_POOL_SIZE = int(os.environ.get("SA_POOL_SIZE", "10"))
DEFAULT_POOL_MAX_OVERFLOW = int(os.environ.get("SA_POOL_MAX_OVERFLOW", "30"))


class EngineFactory:
    """Encapsulates creation and management of SQLAlchemy engines."""

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
                pool_kwargs: dict = {}
                if not connection_string.startswith("sqlite"):
                    # SQLite uses pool classes that do not accept these
                    pool_kwargs = {
                        "pool_size": DEFAULT_POOL_SIZE,
                        "max_overflow": DEFAULT_POOL_MAX_OVERFLOW,
                    }
                engine = sa.create_engine(
                    connection_string,
                    echo=echo,
                    pool_recycle=pool_recycle,
                    pool_pre_ping=True,
                    connect_args=connect_args or {},
                    **pool_kwargs,
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
        frozen = cls._freeze_cache_value(connect_args) if connect_args else ()
        return (connection_string, echo, pool_recycle, frozen)

    @classmethod
    def _freeze_cache_value(cls, value: object) -> object:
        """Convert nested mapping and collection values into hashable cache keys."""
        if isinstance(value, Mapping):
            return frozenset(
                (key, cls._freeze_cache_value(item)) for key, item in value.items()
            )
        if isinstance(value, (list, tuple)):
            return tuple(cls._freeze_cache_value(item) for item in value)
        if isinstance(value, (set, frozenset)):
            return frozenset(cls._freeze_cache_value(item) for item in value)
        hash(value)
        return value
