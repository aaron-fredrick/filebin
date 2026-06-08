"""Structured exception hierarchy for the filebin SDK.

All exceptions carry contextual fields rather than just a string message,
enabling programmatic error handling without string parsing.
"""

from __future__ import annotations


class FilebinError(Exception):
    """Base class for all filebin SDK exceptions."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        bin_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.bin_id = bin_id

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.status_code is not None:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)


class NetworkError(FilebinError):
    """Raised when the underlying aiohttp transport fails (connection error, DNS, etc.)."""


class TimeoutError(FilebinError):
    """Raised when a request exceeds the configured timeout."""


class RateLimitError(FilebinError):
    """Raised on HTTP 429 — Too Many Requests."""

    def __init__(self, retry_after: int | None = None) -> None:
        msg = "Rate limited by Filebin.net"
        if retry_after is not None:
            msg += f" — retry after {retry_after}s"
        super().__init__(msg, status_code=429)
        self.retry_after = retry_after


class ServerError(FilebinError):
    """Raised on HTTP 5xx responses."""

    def __init__(self, status_code: int, body: str = "") -> None:
        super().__init__(f"Server error: {body or 'no detail'}", status_code=status_code)


class AuthenticationError(FilebinError):
    """Raised on HTTP 403 when access is denied."""

    def __init__(self, reason: str, bin_id: str | None = None) -> None:
        super().__init__(f"Access denied: {reason}", status_code=403, bin_id=bin_id)


class ApprovalRequiredError(AuthenticationError):
    """Raised on HTTP 403 when a bin requires approval before files can be downloaded."""

    def __init__(self, bin_id: str | None = None) -> None:
        super().__init__("This bin requires approval before files can be downloaded.", bin_id=bin_id)


class FileDownloadLimitError(AuthenticationError):
    """Raised on HTTP 403 when files or bins have exceeded the download limit."""

    def __init__(self, bin_id: str | None = None) -> None:
        super().__init__("The file has been requested too many times or exceeded limits.", bin_id=bin_id)


class BinNotFoundError(FilebinError):
    """Raised when a requested bin does not exist or has expired."""

    def __init__(self, bin_id: str) -> None:
        super().__init__(f"Bin not found: {bin_id!r}", status_code=404, bin_id=bin_id)


class FileNotFoundError(FilebinError):
    """Raised when a requested file does not exist within a bin."""

    def __init__(self, bin_id: str, filename: str) -> None:
        super().__init__(
            f"File not found: {filename!r} in bin {bin_id!r}",
            status_code=404,
            bin_id=bin_id,
        )
        self.filename = filename


class BinLockedError(FilebinError):
    """Raised when attempting to upload to a locked (read-only) bin."""

    def __init__(self, bin_id: str) -> None:
        super().__init__(f"Bin is locked (read-only): {bin_id!r}", status_code=404, bin_id=bin_id)


class StorageFullError(FilebinError):
    """Raised on HTTP 403 or 507 when the bin has no remaining storage capacity."""

    def __init__(self, bin_id: str) -> None:
        super().__init__(f"Storage full for bin: {bin_id!r}", status_code=507, bin_id=bin_id)


class UploadValidationError(FilebinError):
    """Raised on HTTP 400 or 411 when file upload validation fails (e.g. invalid extension, size, checksums)."""

    def __init__(self, reason: str, bin_id: str | None = None) -> None:
        super().__init__(f"Upload validation failed: {reason}", status_code=400, bin_id=bin_id)
