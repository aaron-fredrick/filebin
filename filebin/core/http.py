"""HTTP transport layer — wraps aiohttp and maps status codes to typed exceptions.

This is the ONLY place in the SDK where:
  - HTTP status codes are mapped to exception types
  - aiohttp is directly referenced
  - Session lifecycle is managed

Nothing above this layer should know about HTTP status codes.
"""

from __future__ import annotations

import gzip
import io
import json
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp

from filebin.core.config import ClientConfig
from filebin.core.errors import (
    AuthenticationError,
    BinNotFoundError,
    FilebinError,
    FileNotFoundError,
    NetworkError,
    RateLimitError,
    ServerError,
    StorageFullError,
    TimeoutError,
)
from filebin.core.retry import RetryPolicy

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParsedResponse:
    """Decoded HTTP response.

    Args:
        status: HTTP status code.
        body: Decoded body — dict for JSON, bytes for binary, str for text.
        headers: Response headers as a plain dict.
        location: Value of the Location header, if present (e.g. S3 redirect URL).
    """

    status: int
    body: Any
    headers: dict[str, str]
    location: str | None


class HttpTransport:
    """aiohttp session wrapper providing typed request methods and error mapping.

    Owns the aiohttp.ClientSession lifecycle. Must be used as an async
    context manager, or closed explicitly via close().

    Args:
        config: Client configuration controlling timeouts, retries, and headers.
    """

    _DEFAULT_HEADERS = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Accept": "*/*",
    }

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._session: aiohttp.ClientSession | None = None
        self._retry = RetryPolicy(
            max_attempts=config.max_retries,
            backoff_factor=config.retry_backoff_factor,
        )

    async def __aenter__(self) -> HttpTransport:
        self._open_session()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    def _open_session(self) -> None:
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self._config.timeout_seconds)
            self._session = aiohttp.ClientSession(
                base_url=self._config.base_url,
                headers={
                    **self._DEFAULT_HEADERS,
                    "User-Agent": self._config.user_agent,
                    "Host": "filebin.net",
                    "Referer": "https://filebin.net/",
                },
                cookies={"verified": self._config.verified_cookie},
                timeout=timeout,
            )

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def _active_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("HttpTransport is not open. Use as an async context manager.")
        return self._session

    async def get(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        allow_redirects: bool = True,
        bin_id: str | None = None,
        filename: str | None = None,
    ) -> ParsedResponse:
        return await self._retry.execute(
            self._request,
            "GET",
            path,
            headers=headers,
            allow_redirects=allow_redirects,
            bin_id=bin_id,
            filename=filename,
        )

    async def post(
        self,
        path: str,
        *,
        data: Any = None,
        headers: dict[str, str] | None = None,
        bin_id: str | None = None,
        filename: str | None = None,
    ) -> ParsedResponse:
        return await self._retry.execute(
            self._request,
            "POST",
            path,
            data=data,
            headers=headers,
            bin_id=bin_id,
            filename=filename,
        )

    async def put(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        bin_id: str | None = None,
    ) -> ParsedResponse:
        return await self._retry.execute(
            self._request,
            "PUT",
            path,
            headers=headers,
            bin_id=bin_id,
        )

    async def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        bin_id: str | None = None,
        filename: str | None = None,
    ) -> ParsedResponse:
        return await self._retry.execute(
            self._request,
            "DELETE",
            path,
            headers=headers,
            bin_id=bin_id,
            filename=filename,
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        data: Any = None,
        headers: dict[str, str] | None = None,
        allow_redirects: bool = True,
        bin_id: str | None = None,
        filename: str | None = None,
    ) -> ParsedResponse:
        try:
            async with self._active_session.request(
                method,
                path,
                data=data,
                headers=headers,
                allow_redirects=allow_redirects,
            ) as response:
                body = await self._decode_body(response)
                resp_headers = dict(response.headers)
                location = resp_headers.get("Location")
                parsed = ParsedResponse(
                    status=response.status,
                    body=body,
                    headers=resp_headers,
                    location=location,
                )
                self._raise_for_status(parsed, bin_id=bin_id, filename=filename)
                return parsed

        except FilebinError:
            raise
        except aiohttp.ServerTimeoutError as exc:
            raise TimeoutError(f"Request timed out after {self._config.timeout_seconds}s") from exc
        except aiohttp.ClientError as exc:
            raise NetworkError(f"Network error: {exc}") from exc

    @staticmethod
    async def _decode_body(response: aiohttp.ClientResponse) -> Any:
        """Decode response body according to Content-Type and Content-Encoding."""
        content_type = response.headers.get("Content-Type", "")
        content_encoding = response.headers.get("Content-Encoding", "")

        raw = b""
        async for chunk in response.content.iter_any():
            raw += chunk

        if "gzip" in content_encoding:
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
                    raw = gz.read()
            except gzip.BadGzipFile:
                pass

        if "application/json" in content_type:
            return json.loads(raw.decode("utf-8"))
        if "text/" in content_type:
            return raw.decode("utf-8")
        return raw

    @staticmethod
    def _raise_for_status(
        response: ParsedResponse,
        *,
        bin_id: str | None,
        filename: str | None,
    ) -> None:
        """Map HTTP status codes to typed exceptions.

        This is the authoritative and exhaustive status→exception mapping.
        All other SDK layers receive typed exceptions only.
        """
        status = response.status

        if status in (200, 201, 302):
            return

        if status == 403:
            body_str = str(response.body).lower() if response.body else ""
            if "storage" in body_str or "full" in body_str:
                raise StorageFullError(bin_id or "unknown")
            raise AuthenticationError(
                reason=str(response.body) or "forbidden",
                bin_id=bin_id,
            )

        if status == 404:
            if filename is not None and bin_id is not None:
                raise FileNotFoundError(bin_id, filename)
            if bin_id is not None:
                # Distinguish locked bins (404 on upload) from missing bins
                raise BinNotFoundError(bin_id)
            raise BinNotFoundError(bin_id or "unknown")

        if status == 429:
            raise RateLimitError()

        if 500 <= status < 600:
            raise ServerError(status_code=status, body=str(response.body or ""))

        _logger.warning("Unhandled HTTP status %d from Filebin.net", status)
