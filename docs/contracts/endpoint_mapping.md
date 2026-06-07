# Endpoint Mapping

This table maps the Filebin.net OpenAPI endpoints to the Python SDK methods.

| OpenAPI Endpoint | HTTP Method | SDK Method | Response Model |
|---|---|---|---|
| `/{bin}/{filename}` | GET | `download_file(bin, filename)` | `Path` (file saved to disk) |
| `/{bin}/{filename}` | POST | `upload_file(bin, path)` | `FileModel` |
| `/{bin}/{filename}` | DELETE | `delete_file(bin, filename)` | `None` |
| `/{bin}` | GET | `list_bin(bin)` | `BinModel` |
| `/{bin}` | DELETE | `delete_bin(bin)` | `None` |
| `/{bin}` | PUT | `lock_bin(bin)` | `BinModel` |
| `/archive/{bin}/zip` | GET | `download_archive(bin, "zip")` | `Path` |
| `/archive/{bin}/tar` | GET | `download_archive(bin, "tar")` | `Path` |
| `/qr/{bin}` | GET | `*Not natively mapped*` | `QRModel` (if `[qr]` installed) |
