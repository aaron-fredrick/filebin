import datetime

from filebin.models.bin import BinModel
from filebin.models.file import FileModel

import pytest

pytestmark = pytest.mark.unit


def test_file_from_api_dict(sample_file_data: dict) -> None:
    file = FileModel.from_api_dict(sample_file_data)
    assert file.filename == "test.txt"
    assert file.content_type == "text/plain"
    assert file.bytes == 512
    assert file.md5 == "abc"
    assert file.sha256 == "def"
    assert isinstance(file.created_at, datetime.datetime)
    assert file.created_at.year == 2024


def test_bin_from_api_dict(sample_bin_data: dict) -> None:
    bin_model = BinModel.from_api_dict(sample_bin_data)
    assert bin_model.id == "test-bin-123"
    assert bin_model.readonly is False
    assert bin_model.bytes == 1024
    assert isinstance(bin_model.created_at, datetime.datetime)
    assert isinstance(bin_model.expired_at, datetime.datetime)

    assert len(bin_model.files) == 1
    assert bin_model.files[0].filename == "test.txt"


def test_file_missing_optional_fields() -> None:
    # Minimal valid payload
    file = FileModel.from_api_dict({"filename": "bare.txt"})
    assert file.filename == "bare.txt"
    assert file.content_type is None
    assert file.bytes is None
    assert file.md5 is None
    assert file.created_at is None


def test_bin_missing_files() -> None:
    bin_model = BinModel.from_api_dict({"bin": {"id": "bare"}})
    assert bin_model.id == "bare"
    assert bin_model.files == []
