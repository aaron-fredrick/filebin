import hashlib
import uuid
from pathlib import Path

import pytest

from filebin.client.async_client import AsyncFilebinClient

pytestmark = pytest.mark.network


@pytest.mark.asyncio
async def test_file_lifecycle(tmp_path: Path) -> None:
    bin_id = f"test-file-{uuid.uuid4().hex[:8]}"
    content = b"random binary data \x00\x01\x02"

    upload_file = tmp_path / "data.bin"
    upload_file.write_bytes(content)
    expected_sha256 = hashlib.sha256(content).hexdigest()

    async with AsyncFilebinClient() as client:
        # 1. Upload
        file_model = await client.upload_file(bin_id, upload_file)
        assert file_model.filename == "data.bin"
        assert file_model.sha256 == expected_sha256

        # 2. Download
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        dest_path = await client.download_file(bin_id, "data.bin", download_dir)

        assert dest_path.read_bytes() == content

        # 3. Delete file
        await client.delete_file(bin_id, "data.bin")

        # 4. Verify file is gone
        from filebin.core.errors import FileNotFoundError

        with pytest.raises(FileNotFoundError):
            await client.download_file(bin_id, "data.bin", download_dir)

        # Clean up bin
        await client.delete_bin(bin_id)
