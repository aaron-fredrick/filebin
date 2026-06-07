"""Unit tests for HttpTransport — mocked at the aiohttp session boundary."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from filebin.core.config import ClientConfig
from filebin.core.errors import (
    AuthenticationError,
    BinNotFoundError,
    FileNotFoundError,
    NetworkError,
    RateLimitError,
    ServerError,
    StorageFullError,
    TimeoutError,
)
from filebin.core.http import HttpTransport, ParsedResponse

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transport(config: ClientConfig | None = None) -> HttpTransport:
    return HttpTransport(config or ClientConfig())


def _make_aiohttp_response(
    status: int = 200,
    body: bytes = b"",
    content_type: str = "application/json",
    content_encoding: str = "",
    location: str | None = None,
) -> MagicMock:
    """Build a minimal aiohttp response mock."""
    response = MagicMock()
    response.status = status

    headers: dict[str, str] = {"Content-Type": content_type}
    if content_encoding:
        headers["Content-Encoding"] = content_encoding
    if location:
        headers["Location"] = location

    response.headers = headers

    async def _iter_any():
        yield body

    response.content = MagicMock()
    response.content.iter_any = _iter_any

    # Make the context manager work
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock()
    return response


def _patch_session(transport: HttpTransport, response: MagicMock) -> None:
    """Inject a mock session onto a transport.

    aiohttp.ClientSession.request() is used as an async context manager:
        async with session.request(...) as resp:
    Using AsyncMock as the return value correctly supports __aenter__/__aexit__.
    """
    ctx = AsyncMock()
    ctx.__aenter__.return_value = response

    session = MagicMock()
    session.request = MagicMock(return_value=ctx)
    transport._session = session  # noqa: SLF001 — intentional test injection


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_context_manager_opens_and_closes_session() -> None:
    transport = _make_transport()
    async with transport:
        assert transport._session is not None  # noqa: SLF001
    assert transport._session is None  # noqa: SLF001


@pytest.mark.asyncio
async def test_open_session_is_idempotent() -> None:
    transport = _make_transport()
    transport._open_session()  # noqa: SLF001
    first_session = transport._session  # noqa: SLF001
    transport._open_session()  # noqa: SLF001
    assert transport._session is first_session  # noqa: SLF001
    await transport.close()


@pytest.mark.asyncio
async def test_close_when_no_session_is_safe() -> None:
    transport = _make_transport()
    await transport.close()  # should not raise


def test_active_session_raises_when_not_open() -> None:
    transport = _make_transport()
    with pytest.raises(RuntimeError, match="not open"):
        _ = transport._active_session  # noqa: SLF001


# ---------------------------------------------------------------------------
# _raise_for_status — status code mapping
# ---------------------------------------------------------------------------


def _parsed(status: int, body: object = None, location: str | None = None) -> ParsedResponse:
    return ParsedResponse(status=status, body=body, headers={}, location=location)


def test_raise_for_status_200_ok() -> None:
    HttpTransport._raise_for_status(_parsed(200), bin_id=None, filename=None)


def test_raise_for_status_201_ok() -> None:
    HttpTransport._raise_for_status(_parsed(201), bin_id=None, filename=None)


def test_raise_for_status_302_ok() -> None:
    HttpTransport._raise_for_status(_parsed(302), bin_id=None, filename=None)


def test_raise_for_status_403_storage_full() -> None:
    with pytest.raises(StorageFullError):
        HttpTransport._raise_for_status(_parsed(403, "storage is full"), bin_id="b", filename=None)


def test_raise_for_status_403_auth_error() -> None:
    with pytest.raises(AuthenticationError):
        HttpTransport._raise_for_status(_parsed(403, "forbidden"), bin_id="b", filename=None)


def test_raise_for_status_404_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        HttpTransport._raise_for_status(_parsed(404), bin_id="b", filename="f.txt")


def test_raise_for_status_404_bin_not_found_with_bin_id() -> None:
    with pytest.raises(BinNotFoundError):
        HttpTransport._raise_for_status(_parsed(404), bin_id="b", filename=None)


def test_raise_for_status_404_bin_not_found_no_ids() -> None:
    with pytest.raises(BinNotFoundError):
        HttpTransport._raise_for_status(_parsed(404), bin_id=None, filename=None)


def test_raise_for_status_429_rate_limit() -> None:
    with pytest.raises(RateLimitError):
        HttpTransport._raise_for_status(_parsed(429), bin_id=None, filename=None)


def test_raise_for_status_500_server_error() -> None:
    with pytest.raises(ServerError):
        HttpTransport._raise_for_status(_parsed(500, "oops"), bin_id=None, filename=None)


def test_raise_for_status_unhandled_logs_warning(caplog) -> None:
    import logging

    with caplog.at_level(logging.WARNING, logger="filebin.core.http"):
        HttpTransport._raise_for_status(_parsed(418), bin_id=None, filename=None)
    assert "418" in caplog.text


# ---------------------------------------------------------------------------
# _decode_body — content type handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_decode_body_json() -> None:
    payload = json.dumps({"key": "value"}).encode()
    response = _make_aiohttp_response(body=payload, content_type="application/json")
    result = await HttpTransport._decode_body(response)
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_decode_body_text() -> None:
    response = _make_aiohttp_response(body=b"hello", content_type="text/plain")
    result = await HttpTransport._decode_body(response)
    assert result == "hello"


@pytest.mark.asyncio
async def test_decode_body_binary() -> None:
    response = _make_aiohttp_response(body=b"\x00\x01\x02", content_type="application/octet-stream")
    result = await HttpTransport._decode_body(response)
    assert result == b"\x00\x01\x02"


@pytest.mark.asyncio
async def test_decode_body_gzip() -> None:
    import gzip as gzip_mod

    original = b'{"key": "zipped"}'
    compressed = gzip_mod.compress(original)
    response = _make_aiohttp_response(
        body=compressed, content_type="application/json", content_encoding="gzip"
    )
    result = await HttpTransport._decode_body(response)
    assert result == {"key": "zipped"}


@pytest.mark.asyncio
async def test_decode_body_bad_gzip_falls_through() -> None:
    response = _make_aiohttp_response(
        body=b"not-gzip", content_type="application/octet-stream", content_encoding="gzip"
    )
    result = await HttpTransport._decode_body(response)
    assert result == b"not-gzip"


# ---------------------------------------------------------------------------
# HTTP verbs — full request path via mocked session
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_request() -> None:
    transport = _make_transport()
    response = _make_aiohttp_response(body=b'{"ok": true}', status=200)
    _patch_session(transport, response)

    result = await transport.get("/test-bin", bin_id="test-bin")

    assert result.status == 200
    assert result.body == {"ok": True}


@pytest.mark.asyncio
async def test_post_request() -> None:
    transport = _make_transport()
    response = _make_aiohttp_response(body=b'{"file": {}}', status=200)
    _patch_session(transport, response)

    result = await transport.post(
        "/test-bin/f.txt", data=b"hello", bin_id="test-bin", filename="f.txt"
    )

    assert result.status == 200


@pytest.mark.asyncio
async def test_put_request() -> None:
    transport = _make_transport()
    response = _make_aiohttp_response(body=b'{"bin": {}}', status=200)
    _patch_session(transport, response)

    result = await transport.put("/test-bin", bin_id="test-bin")

    assert result.status == 200


@pytest.mark.asyncio
async def test_delete_request() -> None:
    transport = _make_transport()
    response = _make_aiohttp_response(body=b"", status=200, content_type="text/plain")
    _patch_session(transport, response)

    result = await transport.delete("/test-bin", bin_id="test-bin")

    assert result.status == 200


@pytest.mark.asyncio
async def test_request_maps_timeout_to_typed_error() -> None:
    import aiohttp as _aiohttp

    transport = _make_transport()
    session = MagicMock()
    session.request = MagicMock(side_effect=_aiohttp.ServerTimeoutError())
    transport._session = session  # noqa: SLF001

    with pytest.raises(TimeoutError, match="timed out"):
        await transport.get("/test-bin", bin_id="test-bin")


@pytest.mark.asyncio
async def test_request_maps_client_error_to_network_error() -> None:
    import aiohttp as _aiohttp

    transport = _make_transport()
    session = MagicMock()
    session.request = MagicMock(side_effect=_aiohttp.ClientError("conn failed"))
    transport._session = session  # noqa: SLF001

    with pytest.raises(NetworkError, match="Network error"):
        await transport.get("/test-bin", bin_id="test-bin")


@pytest.mark.asyncio
async def test_request_propagates_filebin_errors() -> None:
    transport = _make_transport()
    response = _make_aiohttp_response(body=b"", status=404, content_type="text/plain")
    _patch_session(transport, response)

    with pytest.raises(BinNotFoundError):
        await transport.get("/missing-bin", bin_id="missing-bin")
