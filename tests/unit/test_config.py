import dataclasses

import pytest

from filebin.core.config import ClientConfig

pytestmark = pytest.mark.unit


def test_config_defaults() -> None:
    config = ClientConfig()
    assert config.base_url == "https://filebin.net"
    assert config.timeout_seconds == 30.0
    assert config.max_retries == 3
    assert config.retry_backoff_factor == 0.5
    assert "filebin-python/" in config.user_agent
    assert config.verified_cookie == "2024-05-24"


def test_config_frozen() -> None:
    config = ClientConfig()
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.timeout_seconds = 10.0  # type: ignore


def test_config_validation() -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        ClientConfig(timeout_seconds=0)

    with pytest.raises(ValueError, match="max_retries must be >= 0"):
        ClientConfig(max_retries=-1)

    with pytest.raises(ValueError, match="retry_backoff_factor must be >= 0"):
        ClientConfig(retry_backoff_factor=-0.1)
