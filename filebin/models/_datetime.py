"""Datetime parsing utility."""

from __future__ import annotations

from datetime import datetime

_DATETIME_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
)


def parse_datetime(raw: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string from Filebin API.

    Args:
        raw: The raw datetime string, or None.

    Returns:
        The parsed datetime object, or None if raw is None or unparseable.
    """
    if not raw:
        return None

    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    return None
