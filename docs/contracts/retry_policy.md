# Retry Policy Contract

This document details the exact retry behaviour implemented in the `filebin` SDK via `RetryPolicy`.

## Core Logic
The SDK uses an **exponential backoff with jitter** strategy.
By default, operations are retried up to **3 times** with a backoff factor of **0.5s**.

`delay = min(backoff_factor * (2 ^ attempt), 60s) + jitter`
where `jitter` is a random value up to 10% of the base delay.

## Retryable Exceptions
The SDK **will** retry if one of the following is encountered:

* `NetworkError` (e.g. DNS failure, connection reset, connection refused)
* `TimeoutError` (request exceeded the configured `timeout_seconds`)
* `RateLimitError` (HTTP 429)
* `ServerError` (HTTP 5xx, e.g. 502 Bad Gateway, 503 Service Unavailable)

## Non-Retryable Exceptions (Fail-fast)
The SDK will **never** retry the following exceptions, as their state is unlikely to change without intervention:

* `BinNotFoundError` (HTTP 404 on a bin)
* `FileNotFoundError` (HTTP 404 on a file)
* `AuthenticationError` (HTTP 403 on download limit, unapproved bin)
* `BinLockedError` (HTTP 404 on upload to locked bin)
* `StorageFullError` (HTTP 403 when storage quota is exhausted)
