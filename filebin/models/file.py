"""File model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from filebin.models._datetime import parse_datetime


@dataclass(frozen=True)
class FileModel:
    """Represents a single file stored inside a Filebin bin."""

    filename: str
    content_type: str | None
    bytes: int | None
    md5: str | None
    sha256: str | None
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_api_dict(cls, data: dict[str, str | int | None]) -> FileModel:
        """Parse a FileModel from a Filebin API dict."""
        return cls(
            filename=str(data.get("filename", "")),
            content_type=str(data["content-type"]) if "content-type" in data else None,
            bytes=int(data["bytes"]) if "bytes" in data and data["bytes"] is not None else None,
            md5=str(data["md5"]) if "md5" in data else None,
            sha256=str(data["sha256"]) if "sha256" in data else None,
            created_at=parse_datetime(str(data.get("created_at")))
            if data.get("created_at")
            else None,
            updated_at=parse_datetime(str(data.get("updated_at")))
            if data.get("updated_at")
            else None,
        )
