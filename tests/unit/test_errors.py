from filebin.core.errors import (
    AuthenticationError,
    BinNotFoundError,
    FileNotFoundError,
    RateLimitError,
    ServerError,
)


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
