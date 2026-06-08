import pytest

from filebin.core.errors import (
    ApprovalRequiredError,
    AuthenticationError,
    BinNotFoundError,
    FileDownloadLimitError,
    FileNotFoundError,
    RateLimitError,
    ServerError,
    StorageFullError,
    UploadValidationError,
)

pytestmark = pytest.mark.unit


def test_bin_not_found() -> None:
    exc = BinNotFoundError("test-123")
    assert exc.bin_id == "test-123"
    assert exc.status_code == 404
    assert str(exc) == "Bin not found: 'test-123' (HTTP 404)"


def test_file_not_found() -> None:
    exc = FileNotFoundError("test-123", "test.txt")
    assert exc.bin_id == "test-123"
    assert exc.filename == "test.txt"
    assert exc.status_code == 404
    assert str(exc) == "File not found: 'test.txt' in bin 'test-123' (HTTP 404)"


def test_rate_limit() -> None:
    exc = RateLimitError(retry_after=10)
    assert exc.retry_after == 10
    assert exc.status_code == 429
    assert str(exc) == "Rate limited by Filebin.net — retry after 10s (HTTP 429)"


def test_server_error() -> None:
    exc = ServerError(status_code=502, body="Bad Gateway")
    assert exc.status_code == 502
    assert str(exc) == "Server error: Bad Gateway (HTTP 502)"


def test_authentication_error() -> None:
    exc = AuthenticationError("Download limit reached", bin_id="test-123")
    assert exc.status_code == 403
    assert exc.bin_id == "test-123"
    assert str(exc) == "Access denied: Download limit reached (HTTP 403)"


def test_approval_required_error() -> None:
    exc = ApprovalRequiredError(bin_id="test-123")
    assert exc.status_code == 403
    assert exc.bin_id == "test-123"
    assert "requires approval" in str(exc)


def test_file_download_limit_error() -> None:
    exc = FileDownloadLimitError(bin_id="test-123")
    assert exc.status_code == 403
    assert exc.bin_id == "test-123"
    assert "exceeded limits" in str(exc)


def test_storage_full_error() -> None:
    exc = StorageFullError(bin_id="test-123")
    assert exc.status_code == 507
    assert exc.bin_id == "test-123"
    assert "Storage full" in str(exc)


def test_upload_validation_error() -> None:
    exc = UploadValidationError("File too large", bin_id="test-123")
    assert exc.status_code == 400
    assert exc.bin_id == "test-123"
    assert "Validation failed" in str(exc) or "Upload validation failed: File too large" in str(exc)
