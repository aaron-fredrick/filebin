"""Primary async client for the Filebin SDK."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from filebin.core.config import ClientConfig
from filebin.core.http import HttpTransport
from filebin.models.bin import BinModel
from filebin.models.file import FileModel


class AsyncFilebinClient:
    """Async SDK client for the Filebin.net REST API.

    Must be used as an async context manager or closed explicitly:
        async with AsyncFilebinClient() as client:
            await client.list_bin("my-bin")
    """

    def __init__(self, config: ClientConfig | None = None) -> None:
        self.config = config or ClientConfig()
        self._transport = HttpTransport(self.config)

    async def __aenter__(self) -> AsyncFilebinClient:
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._transport.__aexit__()

    async def close(self) -> None:
        """Close the underlying HTTP transport session."""
        await self._transport.close()

    async def upload_file(self, bin_id: str, path: Path | str) -> FileModel:
        """Upload a local file to a bin."""
        path_obj = Path(path)
        with path_obj.open("rb") as f:
            data = f.read()

        filename = path_obj.name
        headers = {"bin": bin_id, "filename": filename}
        response = await self._transport.post(
            f"/{bin_id}/{filename}",
            data=data,
            headers=headers,
            bin_id=bin_id,
            filename=filename,
        )
        return FileModel.from_api_dict(response.body["file"])

    async def download_file(self, bin_id: str, filename: str, dest_dir: Path | str) -> Path:
        """Download a file from a bin to a local directory."""
        dest_path = Path(dest_dir) / filename
        response = await self._transport.get(
            f"/{bin_id}/{filename}",
            bin_id=bin_id,
            filename=filename,
        )
        with dest_path.open("wb") as f:
            f.write(response.body)
        return dest_path

    async def delete_file(self, bin_id: str, filename: str) -> None:
        """Delete a single file from a bin."""
        await self._transport.delete(
            f"/{bin_id}/{filename}",
            bin_id=bin_id,
            filename=filename,
        )

    async def list_bin(self, bin_id: str) -> BinModel:
        """Retrieve metadata and files for a bin."""
        response = await self._transport.get(f"/{bin_id}", bin_id=bin_id)
        return BinModel.from_api_dict(response.body)

    async def lock_bin(self, bin_id: str) -> BinModel:
        """Lock a bin (mark as read-only)."""
        response = await self._transport.put(f"/{bin_id}", bin_id=bin_id)
        return BinModel.from_api_dict(response.body)

    async def delete_bin(self, bin_id: str) -> None:
        """Delete an entire bin and all its files."""
        await self._transport.delete(f"/{bin_id}", bin_id=bin_id)

    async def download_archive(
        self,
        bin_id: str,
        fmt: Literal["zip", "tar"],
        dest_dir: Path | str,
    ) -> Path:
        """Download all files in a bin as a single archive."""
        dest_path = Path(dest_dir) / f"{bin_id}.{fmt}"
        response = await self._transport.get(
            f"/archive/{bin_id}/{fmt}",
            bin_id=bin_id,
        )
        with dest_path.open("wb") as f:
            f.write(response.body)
        return dest_path
