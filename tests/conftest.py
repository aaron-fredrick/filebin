"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock

import pytest

from filebin.core.config import ClientConfig
from filebin.core.http import HttpTransport


@pytest.fixture
def client_config() -> ClientConfig:
    """Provide a fast ClientConfig for testing (no retries, short timeout)."""
    return ClientConfig(
        base_url="https://api.test",
        timeout_seconds=0.1,
        max_retries=0,
        retry_backoff_factor=0.0,
    )


@pytest.fixture
def mock_transport() -> AsyncMock:
    """Provide a fully mocked HttpTransport."""
    transport = AsyncMock(spec=HttpTransport)
    # Async context manager mocks
    transport.__aenter__.return_value = transport
    transport.__aexit__.return_value = None
    return transport


@pytest.fixture
def sample_bin_data() -> dict:
    return {
        "bin": {
            "id": "test-bin-123",
            "readonly": False,
            "bytes": 1024,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "expired_at": "2024-01-07T12:00:00Z",
        },
        "files": [
            {
                "filename": "test.txt",
                "content-type": "text/plain",
                "bytes": 512,
                "created_at": "2024-01-01T12:00:00Z",
                "md5": "abc",
                "sha256": "def",
            }
        ],
    }


@pytest.fixture
def sample_file_data() -> dict:
    return {
        "filename": "test.txt",
        "content-type": "text/plain",
        "bytes": 512,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "md5": "abc",
        "sha256": "def",
    }
