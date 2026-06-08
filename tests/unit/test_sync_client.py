import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from filebin.client.sync_client import FilebinClient, _guard_no_running_loop
from filebin.core.errors import BinNotFoundError
from filebin.models.bin import BinModel
from filebin.models.file import FileModel

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_async_client():
    with patch("filebin.client.sync_client.AsyncFilebinClient", autospec=True) as mock_cls:
        instance = mock_cls.return_value
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock()
        instance.list_bin = AsyncMock()
        instance.lock_bin = AsyncMock()
        instance.delete_bin = AsyncMock()
        instance.upload_file = AsyncMock()
        instance.download_file = AsyncMock()
        instance.delete_file = AsyncMock()
        instance.download_archive = AsyncMock()
        yield instance


@pytest.fixture
def client():
    return FilebinClient()


def test_guard_no_running_loop_passes_outside_event_loop() -> None:
    _guard_no_running_loop()  # Should not raise


def test_guard_no_running_loop_raises_inside_event_loop() -> None:
    async def _inner() -> None:
        with pytest.raises(RuntimeError, match="AsyncFilebinClient"):
            _guard_no_running_loop()

    asyncio.run(_inner())


def test_list_bin(client, mock_async_client) -> None:
    mock_async_client.list_bin.return_value = BinModel.from_api_dict({"bin": {"id": "test-bin"}})
    result = client.list_bin("test-bin")
    assert isinstance(result, BinModel)
    mock_async_client.list_bin.assert_awaited_once_with("test-bin")


def test_lock_bin(client, mock_async_client) -> None:
    mock_async_client.lock_bin.return_value = BinModel.from_api_dict({"bin": {"id": "test-bin"}})
    result = client.lock_bin("test-bin")
    assert isinstance(result, BinModel)
    mock_async_client.lock_bin.assert_awaited_once_with("test-bin")


def test_delete_bin(client, mock_async_client) -> None:
    mock_async_client.delete_bin.return_value = None
    client.delete_bin("test-bin")
    mock_async_client.delete_bin.assert_awaited_once_with("test-bin")


def test_delete_file(client, mock_async_client) -> None:
    mock_async_client.delete_file.return_value = None
    client.delete_file("test-bin", "test.txt")
    mock_async_client.delete_file.assert_awaited_once_with("test-bin", "test.txt")


def test_upload_file(client, mock_async_client, tmp_path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello")
    mock_async_client.upload_file.return_value = FileModel.from_api_dict({"filename": "test.txt"})
    result = client.upload_file("test-bin", test_file)
    assert isinstance(result, FileModel)
    mock_async_client.upload_file.assert_awaited_once_with("test-bin", test_file)


def test_download_file(client, mock_async_client, tmp_path) -> None:
    expected_path = tmp_path / "test.txt"
    mock_async_client.download_file.return_value = expected_path
    result = client.download_file("test-bin", "test.txt", tmp_path)
    assert result == expected_path
    mock_async_client.download_file.assert_awaited_once_with("test-bin", "test.txt", tmp_path)


def test_download_archive(client, mock_async_client, tmp_path) -> None:
    expected_path = tmp_path / "test-bin.zip"
    mock_async_client.download_archive.return_value = expected_path
    result = client.download_archive("test-bin", "zip", tmp_path)
    assert result == expected_path
    mock_async_client.download_archive.assert_awaited_once_with("test-bin", "zip", tmp_path)


def test_create_bin_returns_existing_bin(client) -> None:
    """When the bin exists, create_bin should return the fetched metadata."""
    existing = BinModel.from_api_dict({"bin": {"id": "existing-bin"}, "files": []})
    with patch.object(FilebinClient, "list_bin", return_value=existing):
        result = client.create_bin("existing-bin")
    assert isinstance(result, BinModel)
    assert result.id == "existing-bin"


def test_create_bin_returns_shell_for_new_bin(client) -> None:
    """When the bin does not exist, create_bin should return a shell BinModel."""
    with patch.object(FilebinClient, "list_bin", side_effect=BinNotFoundError("new-bin-01")):
        result = client.create_bin("new-bin-01")
    assert isinstance(result, BinModel)
    assert result.id == "new-bin-01"
    assert result.files == []
    assert result.bytes == 0


def test_create_bin_generates_id_when_none_provided(client) -> None:
    """When no bin_id is provided, create_bin should auto-generate one."""
    with patch.object(FilebinClient, "list_bin", side_effect=BinNotFoundError("auto")):
        result = client.create_bin()
    assert isinstance(result, BinModel)
    assert len(result.id) == 16


def test_create_bin_raises_on_invalid_id(client) -> None:
    """An invalid custom bin_id should raise ValueError without a network call."""
    with patch.object(FilebinClient, "list_bin") as mock_list_bin:
        with pytest.raises(ValueError):
            client.create_bin("!!invalid!!")
        mock_list_bin.assert_not_called()
