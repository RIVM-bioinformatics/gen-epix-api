"""Verify Alembic URL handling for seqdb migrations."""

import runpy
from contextlib import nullcontext
from pathlib import Path

import alembic.context
import pytest
from alembic.config import Config

SOURCE_PATH = (
    Path(__file__).resolve().parents[5]
    / "gen_epix"
    / "seqdb"
    / "repositories"
    / "sa_alembic"
    / "env.py"
)


def test_offline_migrations_preserve_percent_encoded_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep percent-encoded credentials intact through ConfigParser interpolation."""
    url = "postgresql://user:p%40ss@localhost/database"
    config = Config()
    configured_urls: list[str] = []
    monkeypatch.setattr(alembic.context, "config", config, raising=False)
    monkeypatch.setattr(alembic.context, "get_x_argument", lambda **_: {})
    monkeypatch.setattr(alembic.context, "is_offline_mode", lambda: True)
    monkeypatch.setattr(
        alembic.context,
        "configure",
        lambda **kwargs: configured_urls.append(kwargs["url"]),
    )
    monkeypatch.setattr(alembic.context, "begin_transaction", nullcontext)
    monkeypatch.setattr(alembic.context, "run_migrations", lambda: None)
    monkeypatch.setenv("ALEMBIC_URL", url)

    runpy.run_path(str(SOURCE_PATH))

    assert configured_urls == [url]
    assert config.get_main_option("sqlalchemy.url") == url
