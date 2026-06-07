"""Client configuration dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field

from filebin.__version__ import __version__


@dataclass(frozen=True)
class ClientConfig:
    """Immutable configuration for the Filebin SDK client.

    All fields have production-safe defaults. Construct a custom instance
    only when overriding transport behaviour (e.g. test environments).

    Args:
        base_url: Base URL for all API requests.
        timeout_seconds: Per-request timeout. Raises TimeoutError when exceeded.
        max_retries: Maximum retry attempts for retryable failures.
        retry_backoff_factor: Multiplier for exponential backoff between retries.
        user_agent: Value sent in the User-Agent request header.
        verified_cookie: Value for the `verified` session cookie required by Filebin.net.
    """

    base_url: str = "https://filebin.net"
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 0.5
    user_agent: str = field(default_factory=lambda: f"filebin-python/{__version__}")
    verified_cookie: str = "2024-05-24"

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got {self.timeout_seconds}")
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {self.max_retries}")
        if self.retry_backoff_factor < 0:
            raise ValueError(f"retry_backoff_factor must be >= 0, got {self.retry_backoff_factor}")
