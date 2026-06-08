from unittest.mock import AsyncMock, patch

import pytest

from filebin.client.async_client import AsyncFilebinClient
from filebin.core.errors import BinNotFoundError
from filebin.models.bin import BinModel
from filebin.models.file import FileModel

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_transport():
    with patch("filebin.client.async_client.HttpTransport", autospec=True) as mock:
        transport_instance = mock.return_value
        transport_instance.get = AsyncMock()
        transport_instance.post = AsyncMock()
        transport_instance.put = AsyncMock()
        transport_instance.delete = AsyncMock()
        transport_instance.__aenter__ = AsyncMock(return_value=transport_instance)
        transport_instance.__aexit__ = AsyncMock()
        transport_instance.close = AsyncMock()
        yield transport_instance


@pytest.fixture
def client(mock_transport):
    return AsyncFilebinClient()


@pytest.mark.asyncio
async def test_context_manager(client, mock_transport) -> None:
    async with client:
        pass
    mock_transport.__aenter__.assert_awaited_once()
    mock_transport.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_close(client, mock_transport) -> None:
    await client.close()
    mock_transport.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_bin(client, mock_transport) -> None:
    mock_response = AsyncMock()
    mock_response.body = {"bin": {"id": "test-bin"}}
    mock_transport.get.return_value = mock_response

    result = await client.list_bin("test-bin")

    assert isinstance(result, BinModel)
    mock_transport.get.assert_awaited_once_with("/test-bin", bin_id="test-bin")


@pytest.mark.asyncio
async def test_lock_bin(client, mock_transport) -> None:
    mock_response = AsyncMock()
    mock_response.body = {"bin": {"id": "test-bin"}}
    mock_transport.put.return_value = mock_response

    result = await client.lock_bin("test-bin")

    assert isinstance(result, BinModel)
    mock_transport.put.assert_awaited_once_with("/test-bin", bin_id="test-bin")


@pytest.mark.asyncio
async def test_delete_bin(client, mock_transport) -> None:
    await client.delete_bin("test-bin")
    mock_transport.delete.assert_awaited_once_with("/test-bin", bin_id="test-bin")


@pytest.mark.asyncio
async def test_delete_file(client, mock_transport) -> None:
    await client.delete_file("test-bin", "test.txt")
    mock_transport.delete.assert_awaited_once_with(
        "/test-bin/test.txt",
        bin_id="test-bin",
        filename="test.txt",
    )


@pytest.mark.asyncio
async def test_upload_file(client, mock_transport, tmp_path) -> None:
    mock_response = AsyncMock()
    mock_response.body = {"file": {"filename": "test.txt"}}
    mock_transport.post.return_value = mock_response

    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello")

    result = await client.upload_file("test-bin", test_file)

    assert isinstance(result, FileModel)
    mock_transport.post.assert_awaited_once_with(
        "/test-bin/test.txt",
        data=b"hello",
        headers={"bin": "test-bin", "filename": "test.txt"},
        bin_id="test-bin",
        filename="test.txt",
    )


@pytest.mark.asyncio
async def test_download_file(client, mock_transport, tmp_path) -> None:
    mock_response = AsyncMock()
    mock_response.body = b"hello"
    mock_transport.get.return_value = mock_response

    dest = await client.download_file("test-bin", "test.txt", tmp_path)

    assert dest.read_bytes() == b"hello"
    mock_transport.get.assert_awaited_once_with(
        "/test-bin/test.txt",
        bin_id="test-bin",
        filename="test.txt",
    )


@pytest.mark.asyncio
async def test_download_archive(client, mock_transport, tmp_path) -> None:
    mock_response = AsyncMock()
    mock_response.body = b"archive-data"
    mock_transport.get.return_value = mock_response

    dest = await client.download_archive("test-bin", "zip", tmp_path)

    assert dest.read_bytes() == b"archive-data"
    assert dest.name == "test-bin.zip"
    mock_transport.get.assert_awaited_once_with("/archive/test-bin/zip", bin_id="test-bin")


@pytest.mark.asyncio
async def test_create_bin_returns_existing_bin(client, mock_transport) -> None:
    """When the bin already exists, create_bin should return the fetched metadata."""
    mock_response = AsyncMock()
    mock_response.body = {"bin": {"id": "existing-bin"}, "files": []}
    mock_transport.get.return_value = mock_response

    result = await client.create_bin("existing-bin")

    assert isinstance(result, BinModel)
    assert result.id == "existing-bin"
    mock_transport.get.assert_awaited_once_with("/existing-bin", bin_id="existing-bin")


@pytest.mark.asyncio
async def test_create_bin_returns_shell_for_new_bin(client, mock_transport) -> None:
    """When the bin does not exist yet, create_bin should return a shell BinModel."""
    mock_transport.get.side_effect = BinNotFoundError("brand-new-bin")

    result = await client.create_bin("brand-new-bin")

    assert isinstance(result, BinModel)
    assert result.id == "brand-new-bin"
    assert result.files == []
    assert result.bytes == 0


@pytest.mark.asyncio
async def test_create_bin_generates_id_when_none_provided(client, mock_transport) -> None:
    """When no bin_id is given, create_bin should generate a valid one."""
    mock_transport.get.side_effect = BinNotFoundError("auto")

    result = await client.create_bin()

    assert isinstance(result, BinModel)
    assert len(result.id) == 16


@pytest.mark.asyncio
async def test_create_bin_raises_on_invalid_id(client, mock_transport) -> None:
    """An invalid custom bin ID should raise ValueError before any network call."""
    with pytest.raises(ValueError):
        await client.create_bin("!!invalid!!")

    mock_transport.get.assert_not_awaited()
