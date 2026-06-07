# ADR 003: Retry Strategy

## Status
Accepted

## Context
Network instability, intermittent 5xx server errors, and rate limits (429) can cause API operations to fail randomly. A robust SDK should handle transient failures automatically without forcing the caller to implement retry loops.

## Decision
We implemented a strict **exponential backoff with jitter** strategy inside `core/retry.py`.

- **Retried**: `NetworkError`, `TimeoutError`, `RateLimitError`, `ServerError`.
- **Never Retried**: `FileNotFoundError`, `BinNotFoundError`, `AuthenticationError` (deterministic failures).

## Consequences
- The SDK is highly resilient to transient network issues.
- Non-retryable errors fail fast, saving time and resources.
