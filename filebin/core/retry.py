"""Retry policy with exponential backoff and jitter.

The retry contract:

Retryable:
  - NetworkError       (connection failures, DNS, etc.)
  - TimeoutError       (request exceeded timeout)
  - RateLimitError     (HTTP 429)
  - ServerError        (HTTP 5xx)

Never retried:
  - BinNotFoundError   (404 — deterministic)
  - FileNotFoundError  (404 — deterministic)
  - AuthenticationError (403 — no point retrying)
  - BinLockedError     (bin state won't change)
  - StorageFullError   (bin state won't change)

Backoff formula:
  delay = min(backoff_factor * 2^attempt + jitter, MAX_BACKOFF_SECONDS)
  jitter = random float in [0, 0.1 * delay]
"""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from filebin.core.errors import (
    FilebinError,
    NetworkError,
    RateLimitError,
    ServerError,
    TimeoutError,
)

_T = TypeVar("_T")
_logger = logging.getLogger(__name__)

_MAX_BACKOFF_SECONDS = 60.0
_RETRYABLE_TYPES = (NetworkError, TimeoutError, RateLimitError, ServerError)


@dataclass
class RetryPolicy:
    """Exponential backoff retry policy.

    Args:
        max_attempts: Total attempts (1 = no retries).
        backoff_factor: Base multiplier for delay calculation.
    """

    max_attempts: int = 3
    backoff_factor: float = 0.5
    _retryable: tuple[type[FilebinError], ...] = field(
        default=_RETRYABLE_TYPES, init=False, repr=False
    )

    async def execute(
        self,
        coro_fn: Callable[..., Awaitable[_T]],
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """Execute a coroutine with retry on retryable failures.

        Args:
            coro_fn: An async callable to execute.
            *args: Positional arguments forwarded to coro_fn.
            **kwargs: Keyword arguments forwarded to coro_fn.

        Returns:
            The return value of coro_fn on success.

        Raises:
            The last exception if all attempts are exhausted.
        """
        last_exc: Exception | None = None

        for attempt in range(self.max_attempts):
            try:
                return await coro_fn(*args, **kwargs)
            except self._retryable as exc:
                last_exc = exc
                if attempt == self.max_attempts - 1:
                    break
                delay = self._backoff_delay(attempt)
                _logger.debug(
                    "Retryable error on attempt %d/%d — retrying in %.2fs: %s",
                    attempt + 1,
                    self.max_attempts,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
            except FilebinError:
                raise  # Non-retryable — propagate immediately

        raise last_exc  # type: ignore[misc]

    def _backoff_delay(self, attempt: int) -> float:
        base = min(self.backoff_factor * float(2**attempt), _MAX_BACKOFF_SECONDS)
        jitter = random.uniform(0, 0.1 * base)  # noqa: S311 — non-crypto use
        return base + jitter
