# Filebin.net Python SDK

![CI](https://github.com/aaron-fredrick/filebin/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/filebin)

A complete, typed, async-first Python SDK and CLI for the [Filebin.net](https://filebin.net/) API.

## Installation

```bash
pip install filebin
```

With CLI formatting support:
```bash
pip install filebin[cli-pretty]
```

## Quick SDK Usage

```python
import asyncio
from filebin import AsyncFilebinClient

async def main():
    async with AsyncFilebinClient() as client:
        # Upload a file
        file = await client.upload_file("my-bin-id", "document.pdf")
        print(f"Uploaded: {file.filename}")

        # List files in a bin
        bin_meta = await client.list_bin("my-bin-id")
        for f in bin_meta.files:
            print(f.filename)

if __name__ == "__main__":
    asyncio.run(main())
```

## Quick CLI Usage

```bash
# Upload a file
fbin upload document.pdf --bin my-bin-id

# Download a file
fbin download my-bin-id document.pdf

# List contents
fbin list my-bin-id
```

## Documentation

Full documentation is available at: [https://aaron-fredrick.github.io/filebin/](https://aaron-fredrick.github.io/filebin/)
