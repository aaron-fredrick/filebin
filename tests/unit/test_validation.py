import pytest
from filebin.core.validation import generate_bin_id, validate_bin_id


def test_generate_bin_id_length():
    """Test generating a bin ID with various lengths."""
    bin_id = generate_bin_id(16)
    assert len(bin_id) == 16
    
    bin_id = generate_bin_id(60)
    assert len(bin_id) == 60
    
    bin_id = generate_bin_id(8)
    assert len(bin_id) == 8


def test_generate_bin_id_invalid_length():
    """Test generating a bin ID with invalid lengths raises ValueError."""
    with pytest.raises(ValueError, match="must be between 8 and 60"):
        generate_bin_id(7)
        
    with pytest.raises(ValueError, match="must be between 8 and 60"):
        generate_bin_id(61)


def test_validate_bin_id_valid():
    """Test validating valid bin IDs."""
    validate_bin_id("a1b2c3d4e5")
    validate_bin_id("test-bin_123.abc")
    validate_bin_id("12345678")


def test_validate_bin_id_invalid_chars():
    """Test validating bin IDs with invalid characters raises ValueError."""
    with pytest.raises(ValueError, match="invalid characters"):
        validate_bin_id("invalid/bin")
        
    with pytest.raises(ValueError, match="invalid characters"):
        validate_bin_id("invalid@bin")
        
    with pytest.raises(ValueError, match="invalid characters"):
        validate_bin_id("invalid bin")


def test_validate_bin_id_invalid_length():
    """Test validating bin IDs with invalid lengths raises ValueError."""
    with pytest.raises(ValueError, match="too short"):
        validate_bin_id("short")
        
    with pytest.raises(ValueError, match="too long"):
        validate_bin_id("a" * 61)


def test_validate_bin_id_invalid_start():
    """Test validating bin IDs starting with a dot raises ValueError."""
    with pytest.raises(ValueError, match="cannot start with a dot"):
        validate_bin_id(".invalidstart")
