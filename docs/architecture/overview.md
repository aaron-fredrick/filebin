# Architecture Overview

The `filebin` SDK uses a layered architecture designed for maintainability, type-safety, and minimal abstraction depth.

It follows these core principles:
1. **Async-first**: Built on `aiohttp` for modern, non-blocking I/O.
2. **Shallow abstractions**: Max 3 layers deep. No unnecessary "service" or "manager" classes.
3. **Strict separation of concerns**: The HTTP transport layer handles all HTTP logic (retries, error mapping). Models are purely data structures.

## System Layers

- **Client Layer (`filebin.client`)**: Exposes the public API (`AsyncFilebinClient`, `FilebinClient`). Delegates to the core layer.
- **Core Layer (`filebin.core`)**: Manages configuration, handles the raw HTTP transport (`HttpTransport`), parses HTTP status codes into typed exceptions (`errors.py`), and executes the `RetryPolicy`.
- **Model Layer (`filebin.models`)**: Pure data classes (`BinModel`, `FileModel`) that deserialize JSON payloads.

For visual representation, see the C4 diagrams:
- [Context](context.mmd)
- [Container](container.mmd)
- [Component](component.mmd)
