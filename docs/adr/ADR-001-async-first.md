# ADR 001: Async-First Design

## Status
Accepted

## Context
The Filebin.net API is fundamentally an I/O bound service (file uploads and downloads). In Python, synchronous I/O blocks the OS thread, limiting concurrency when dealing with large files or multiple concurrent uploads.

## Decision
The SDK will be designed **async-first** using `aiohttp`. The primary client will be `AsyncFilebinClient`.

To support users who cannot use `asyncio`, we will provide a synchronous wrapper (`FilebinClient`) that uses `asyncio.run()` under the hood. To prevent silent deadlocks if `FilebinClient` is accidentally used inside an active async event loop, a running-loop guard will be implemented to raise a fast `RuntimeError`.

## Consequences
- Better performance and throughput for large file operations.
- Slightly higher cognitive load for users unfamiliar with `async/await`.
- Requires `aiohttp` and `anyio`/`asyncio` knowledge.
