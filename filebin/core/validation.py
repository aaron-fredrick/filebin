"""Validation logic for Filebin bin IDs and filenames."""

import re
import secrets
import string

# Valid characters for generated bin IDs
_ID_CHARS = string.ascii_lowercase + string.digits
# Regex matching invalid characters according to filebin2
_INVALID_BIN_PATTERN = re.compile(r"[^A-Za-z0-9-_.]")


def validate_bin_id(bin_id: str) -> None:
    """Validate a bin ID according to filebin2 constraints.

    Args:
        bin_id: The bin ID to validate.

    Raises:
        ValueError: If the bin ID is invalid.
    """
    if not bin_id:
        raise ValueError("Bin ID cannot be empty.")
    if _INVALID_BIN_PATTERN.search(bin_id):
        raise ValueError("Bin ID contains invalid characters.")
    if len(bin_id) < 8:
        raise ValueError("Bin ID is too short (minimum 8 characters).")
    if len(bin_id) > 60:
        raise ValueError("Bin ID is too long (maximum 60 characters).")
    if bin_id.startswith("."):
        raise ValueError("Bin ID cannot start with a dot.")


def generate_bin_id(length: int = 16) -> str:
    """Generate a random valid bin ID.

    Matches the default behaviour of filebin2 which uses 16 characters
    of lowercase letters and numbers.

    Args:
        length: Length of the generated ID.

    Returns:
        A randomly generated valid bin ID.
    """
    if length < 8 or length > 60:
        raise ValueError("Generated bin length must be between 8 and 60 characters.")
    return "".join(secrets.choice(_ID_CHARS) for _ in range(length))
