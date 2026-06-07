import uuid
from pathlib import Path

import pytest

from filebin.client.async_client import AsyncFilebinClient

pytestmark = pytest.mark.network


@pytest.mark.asyncio
async def test_bin_lifecycle(tmp_path: Path) -> None:
    bin_id = f"test-bin-{uuid.uuid4().hex[:8]}"

    # Create a dummy file
    test_file = tmp_path / "hello.txt"
    test_file.write_text("hello integration test")

    async with AsyncFilebinClient() as client:
        # 1. Upload creates the bin implicitly
        await client.upload_file(bin_id, test_file)

        # 2. List the bin and verify contents
        bin_model = await client.list_bin(bin_id)
        assert bin_model.id == bin_id
        assert not bin_model.readonly
        assert len(bin_model.files) == 1
        assert bin_model.files[0].filename == "hello.txt"

        # 3. Lock the bin
        locked_bin = await client.lock_bin(bin_id)
        assert locked_bin.readonly is True

        # 4. Delete the bin
        await client.delete_bin(bin_id)

        # 5. Verify it's gone
        from filebin.core.errors import BinNotFoundError

        with pytest.raises(BinNotFoundError):
            await client.list_bin(bin_id)
