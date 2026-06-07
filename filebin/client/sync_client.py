"""Synchronous wrapper for the Filebin SDK client."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Literal

from filebin.client.async_client import AsyncFilebinClient
from filebin.core.config import ClientConfig
from filebin.models.bin import BinModel
from filebin.models.file import FileModel


def _guard_no_running_loop() -> None:
    """Ensure we are not running inside an active asyncio event loop.

    Calling asyncio.run() from inside a running loop causes a RuntimeError.
    This guard ensures we fail clearly and explicitly, directing the user
    to the async client instead.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return  # No loop is running, safe to proceed
    raise RuntimeError(
        "FilebinClient cannot be used inside a running async event loop. "
        "Use AsyncFilebinClient instead."
    )


class FilebinClient:
    """Synchronous SDK client for the Filebin.net REST API.

    This is a wrapper around AsyncFilebinClient that uses asyncio.run()
    for all operations. It cannot be used inside an async context.
    """

    def __init__(self, config: ClientConfig | None = None) -> None:
        self.config = config or ClientConfig()

    def upload_file(self, bin_id: str, path: Path | str) -> FileModel:
        """Upload a local file to a bin."""
        _guard_no_running_loop()

        async def _run() -> FileModel:
            async with AsyncFilebinClient(self.config) as client:
                return await client.upload_file(bin_id, path)

        return asyncio.run(_run())

    def download_file(self, bin_id: str, filename: str, dest_dir: Path | str) -> Path:
        """Download a file from a bin to a local directory."""
        _guard_no_running_loop()

        async def _run() -> Path:
            async with AsyncFilebinClient(self.config) as client:
                return await client.download_file(bin_id, filename, dest_dir)

        return asyncio.run(_run())

    def delete_file(self, bin_id: str, filename: str) -> None:
        """Delete a single file from a bin."""
        _guard_no_running_loop()

        async def _run() -> None:
            async with AsyncFilebinClient(self.config) as client:
                await client.delete_file(bin_id, filename)

        return asyncio.run(_run())

    def list_bin(self, bin_id: str) -> BinModel:
        """Retrieve metadata and files for a bin."""
        _guard_no_running_loop()

        async def _run() -> BinModel:
            async with AsyncFilebinClient(self.config) as client:
                return await client.list_bin(bin_id)

        return asyncio.run(_run())

    def lock_bin(self, bin_id: str) -> BinModel:
        """Lock a bin (mark as read-only)."""
        _guard_no_running_loop()

        async def _run() -> BinModel:
            async with AsyncFilebinClient(self.config) as client:
                return await client.lock_bin(bin_id)

        return asyncio.run(_run())

    def delete_bin(self, bin_id: str) -> None:
        """Delete an entire bin and all its files."""
        _guard_no_running_loop()

        async def _run() -> None:
            async with AsyncFilebinClient(self.config) as client:
                await client.delete_bin(bin_id)

        return asyncio.run(_run())

    def download_archive(
        self,
        bin_id: str,
        fmt: Literal["zip", "tar"],
        dest_dir: Path | str,
    ) -> Path:
        """Download all files in a bin as a single archive."""
        _guard_no_running_loop()

        async def _run() -> Path:
            async with AsyncFilebinClient(self.config) as client:
                return await client.download_archive(bin_id, fmt, dest_dir)

        return asyncio.run(_run())
