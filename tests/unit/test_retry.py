import pytest

from filebin.core.errors import BinNotFoundError, NetworkError
from filebin.core.retry import RetryPolicy


@pytest.mark.asyncio
async def test_retry_success_first_try() -> None:
    policy = RetryPolicy()
    calls = 0

    async def _success() -> str:
        nonlocal calls
        calls += 1
        return "ok"

    result = await policy.execute(_success)
    assert result == "ok"
    assert calls == 1


@pytest.mark.asyncio
async def test_retry_success_after_failure() -> None:
    policy = RetryPolicy(max_attempts=3, backoff_factor=0.0)
    calls = 0

    async def _flaky() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise NetworkError("fail")
        return "ok"

    result = await policy.execute(_flaky)
    assert result == "ok"
    assert calls == 3


@pytest.mark.asyncio
async def test_retry_exhausted() -> None:
    policy = RetryPolicy(max_attempts=2, backoff_factor=0.0)
    calls = 0

    async def _always_fail() -> str:
        nonlocal calls
        calls += 1
        raise NetworkError("fail")

    with pytest.raises(NetworkError):
        await policy.execute(_always_fail)
    assert calls == 2


@pytest.mark.asyncio
async def test_retry_non_retryable_propagates_immediately() -> None:
    policy = RetryPolicy(max_attempts=3)
    calls = 0

    async def _fail_404() -> str:
        nonlocal calls
        calls += 1
        raise BinNotFoundError("bin123")

    with pytest.raises(BinNotFoundError):
        await policy.execute(_fail_404)
    assert calls == 1
