"""Optional QR code model.

This is the only module in the SDK permitted to import Pillow.
It is protected by an ImportError guard.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image

    _PILLOW_AVAILABLE = True
except ImportError:
    _PILLOW_AVAILABLE = False


@dataclass(frozen=True)
class QRModel:
    """Represents a QR code image for a bin."""

    raw_bytes: bytes
    bin_id: str

    def __post_init__(self) -> None:
        if not _PILLOW_AVAILABLE:
            raise ImportError(
                "QR features require Pillow. Install the optional dependency: "
                "pip install filebin[qr]"
            )

    @property
    def image(self) -> Image.Image:
        """Return the QR code as a PIL Image."""
        if not _PILLOW_AVAILABLE:
            raise ImportError("pip install filebin[qr] to use QR features.")
        return Image.open(io.BytesIO(self.raw_bytes))

    def show(self) -> None:
        """Display the QR code using the default image viewer."""
        self.image.show()

    def save(self, path: Path | str) -> None:
        """Save the QR code to disk."""
        self.image.save(path)
