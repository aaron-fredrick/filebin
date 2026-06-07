import pytest

from filebin.models.qr import QRModel
from filebin.models.responses import BinResponse, FileUploadResponse

pytestmark = pytest.mark.unit


class TestQRModel:
    def test_instantiation_without_pillow_raises(self, monkeypatch) -> None:
        monkeypatch.setattr("filebin.models.qr._PILLOW_AVAILABLE", False)
        with pytest.raises(ImportError, match="filebin\\[qr\\]"):
            QRModel(raw_bytes=b"data", bin_id="test-bin")

    def test_image_property_without_pillow_raises(self, monkeypatch) -> None:
        import filebin.models.qr as qr_module
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            pytest.skip("Pillow not installed")

        # Build a valid QR model first (Pillow available)
        model = object.__new__(QRModel)
        object.__setattr__(model, "raw_bytes", b"data")
        object.__setattr__(model, "bin_id", "test-bin")

        # Now disable Pillow
        monkeypatch.setattr(qr_module, "_PILLOW_AVAILABLE", False)
        with pytest.raises(ImportError, match="filebin\\[qr\\]"):
            _ = model.image


class TestResponseAliases:
    def test_bin_response_is_dict(self) -> None:
        result: BinResponse = {"bin": {"id": "test"}}
        assert isinstance(result, dict)

    def test_file_upload_response_is_dict(self) -> None:
        result: FileUploadResponse = {"file": {"filename": "test.txt"}}
        assert isinstance(result, dict)
