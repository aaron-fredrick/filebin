"""Bin model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from filebin.models._datetime import parse_datetime
from filebin.models.file import FileModel


@dataclass(frozen=True)
class BinModel:
    """Represents a Filebin bin — a collection of uploaded files."""

    id: str
    readonly: bool
    bytes: int
    created_at: datetime | None
    updated_at: datetime | None
    expired_at: datetime | None
    files: list[FileModel] = field(default_factory=list)

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> BinModel:
        """Parse a BinModel from a Filebin API dict.

        The API usually returns the bin metadata under the 'bin' key
        and the list of files under the 'files' key.
        """
        bin_data = data.get("bin", {})

        # In some contexts, the data might be flat
        if not bin_data and "id" in data:
            bin_data = data

        raw_files = data.get("files", [])
        parsed_files = [FileModel.from_api_dict(f) for f in raw_files]

        return cls(
            id=str(bin_data.get("id", "")),
            readonly=bool(bin_data.get("readonly", False)),
            bytes=int(bin_data.get("bytes", 0)),
            created_at=parse_datetime(str(bin_data.get("created_at")))
            if bin_data.get("created_at")
            else None,
            updated_at=parse_datetime(str(bin_data.get("updated_at")))
            if bin_data.get("updated_at")
            else None,
            expired_at=parse_datetime(str(bin_data.get("expired_at")))
            if bin_data.get("expired_at")
            else None,
            files=parsed_files,
        )
