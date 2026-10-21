import asyncio

import pytest

from gen_epix.util import profile_method


def test_sync_returns_value(tmp_path):
    @profile_method(path=str(tmp_path))
    def sync_add(a, b):
        return a + b

    assert sync_add(1, 2) == 3


def test_sync_writes_log_file(tmp_path):
    @profile_method(path=str(tmp_path))
    def sync_add(a, b):
        return a + b

    sync_add(1, 2)
    logs = list(tmp_path.glob("sync_add-*.log"))
    assert len(logs) == 1
    assert logs[0].stat().st_size > 0


def test_async_returns_value(tmp_path):
    @profile_method(path=str(tmp_path))
    async def async_add(a, b):
        return a + b

    assert asyncio.run(async_add(1, 2)) == 3


def test_async_writes_log_file(tmp_path):
    @profile_method(path=str(tmp_path))
    async def async_add(a, b):
        return a + b

    asyncio.run(async_add(1, 2))
    logs = list(tmp_path.glob("async_add-*.log"))
    assert len(logs) == 1
    assert logs[0].stat().st_size > 0


def test_sync_propagates_exception(tmp_path):
    @profile_method(path=str(tmp_path))
    def boom():
        raise ValueError("oops")

    with pytest.raises(ValueError, match="oops"):
        boom()
    with pytest.raises(ValueError, match="oops"):
        boom()
