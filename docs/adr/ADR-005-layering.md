# ADR 005: Layering Approach

## Status
Accepted

## Context
SDKs often suffer from "service explosion" — abstracting every REST endpoint into a deep tree of Manager/Service classes that obscure the actual HTTP request. This makes the SDK hard to read, trace, and maintain.

## Decision
The `filebin` SDK enforces a strict maximum abstraction depth of 3 layers:

1. **Client**: The public Python API (`AsyncFilebinClient`). Exposes clear, domain-specific methods (`upload_file()`, `list_bin()`).
2. **Core/Transport**: The HTTP abstraction (`HttpTransport`). Handles session lifecycle, retries, headers, and maps HTTP status codes to specific Exceptions.
3. **Models**: Pure data classes.

The Client calls the Transport directly. There are no intermediate `FileService` or `BinManager` classes.

## Consequences
- Code is extremely traceable. You can control-click from the Client method straight into the HTTP execution logic.
- Avoids over-engineering.
