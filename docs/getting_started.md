# Getting Started

## Installation

Filebin.py is available on PyPI. You can install it using pip:

```bash
pip install Filebin.py
```

*Requirements: Python 3.10+*

## Library Usage

To use the library, you should instantiate the `API` client. Since this library is fully asynchronous, the recommended way to use it is within an `async with` context block.

### Basic Example

Here is a simple example showing how to create a bin, upload a file, and download it:

```python
import asyncio
from Filebin import API

async def main():
    async with API() as api:
        # Fetch a bin (creates a reference to an existing or new bin)
        bin = await api.getBin("my-bin-id")
        
        # Upload a file
        file = await bin.uploadFile("report.pdf")
        print(f"Uploaded: {file.name} ({file.bytes} bytes)")
        
        # Download a file to a specific path
        await bin.downloadFile("report.pdf", path="./downloads")
        
        # Lock the bin (make it read-only)
        await api.lockBin("my-bin-id")
        
        # Delete the bin
        await api.deleteBin("my-bin-id")

asyncio.run(main())
```

### Manual Session Management

If you prefer not to use a context manager, you must manually call `start()` and `close()` to manage the underlying HTTP session:

```python
api = API()
await api.start()

bin = await api.getBin("my-bin-id")

# ... do work ...

await api.close()
```

### Response Caching

By default, every call to `api.getBin()` and `api.getFile()` triggers a network request to assure you have the latest state. If you know the state hasn't changed and want to save network overhead, pass `from_cache=True`:

```python
# Network call
bin = await api.getBin("my-bin-id")

# Instant cache retrieval
bin_again = await api.getBin("my-bin-id", from_cache=True)
```
