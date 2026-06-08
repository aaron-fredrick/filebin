# Filebin Python Client & CLI

Welcome to the official documentation for the **Filebin Python Client**. This library provides a complete, typed, async-first Python interface and Command-Line Interface (CLI) for the [Filebin.net](https://filebin.net/) API.

*Note: This is an unofficial, community-driven Python wrapper for Filebin, not affiliated with the official filebin.net service.*

## Key Features

- **Async First:** Built on `aiohttp` for high-performance, non-blocking I/O.
- **Sync Support:** A fully synchronous client (`SyncFilebinClient`) is also provided for standard blocking scripts.
- **Robust Error Handling:** Meticulous mapping of HTTP status codes to Python exceptions (`AuthenticationError`, `UploadValidationError`, etc.) based directly on the Filebin engine.
- **Strict Typing:** Extensively annotated with Python type hints for excellent IDE support and `mypy` compatibility.
- **CLI Included:** A powerful CLI tool (`fbin`) is bundled for easy use directly from your terminal.

## Installation

Install the package via pip:

```bash
pip install filebin
```

To include the rich formatting dependencies for the CLI:

```bash
pip install filebin[cli-pretty]
```

## Quick Start (Python)

### Asynchronous Client

```python
import asyncio
from filebin import AsyncFilebinClient

async def main():
    async with AsyncFilebinClient() as client:
        # Generate a valid local bin ID or validate a custom one
        bin_model = client.create_bin("my-custom-bin-id")
        
        # Upload a file
        file = await client.upload_file(bin_model.id, "document.pdf")
        print(f"Uploaded: {file.filename}")

        # List files in a bin
        bin_meta = await client.list_bin(bin_model.id)
        for f in bin_meta.files:
            print(f.filename)

if __name__ == "__main__":
    asyncio.run(main())
```

### Synchronous Client

```python
from filebin import SyncFilebinClient

client = SyncFilebinClient()

# Create a bin and upload
bin_model = client.create_bin("my-sync-bin")
file = client.upload_file(bin_model.id, "report.csv")
print(f"Uploaded {file.filename} to {bin_model.id}")
```

## Quick Start (CLI)

```bash
# Upload a file (bin ID is automatically generated if omitted)
fbin upload document.pdf --bin my-bin-id

# Download a file
fbin download my-bin-id document.pdf

# List contents
fbin list my-bin-id

# Create a bin
fbin create-bin --bin my-custom-bin-id
```

## Next Steps

- Check out the **[API Reference](api/client.md)** for detailed method signatures.
- Read about the **[CLI Usage](cli/usage.md)**.
- Understand the **[Architecture](architecture/overview.md)** and design decisions behind the client.