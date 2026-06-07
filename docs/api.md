# API Reference

This page describes the core objects in `Filebin.py` and the methods available for interacting with bins and files programmatically.

---

## The `API` Object

This is the main entry point to the Filebin wrapper.

### Initialization

```python
API()
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getBin(bin_id, from_cache=False)` | `Bin` | Fetch a bin by ID |
| `lockBin(bin_id)` | `Bin` | Lock a bin, turning it read-only |
| `deleteBin(bin_id)` | `bool` | Delete a bin completely |
| `downloadZip(bin_id, path)` | `bool` | Download the entire bin as a `.zip` archive to `path` |
| `downloadTar(bin_id, path)` | `bool` | Download the entire bin as a `.tar` archive to `path` |
| `getFile(bin_id, file_name, from_cache=False)` | `File` | Fetch a single file by name from a bin |

---

## The `Bin` Object

Represents a single bin, holding multiple files. Returned by `API.getBin()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Core bin ID |
| `readonly` | `bool` | True if the bin is locked |
| `bytes` | `int` | Total size of the bin in bytes |
| `files` | `List[File]` | Cached list of `File` objects inside this bin |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |
| `expired_at` | `datetime` | Timestamp of expiration |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `uploadFile(file_path)` | `File` | Upload a local file |
| `downloadFile(file_name, path)` | `bool` | Download a file from this bin to a specific local path |
| `deleteFile(file_name)` | `bool` | Delete a single file |
| `downloadZip(path)` | `bool` | Download the bin as a `.zip` |
| `downloadTar(path)` | `bool` | Download the bin as a `.tar` |
| `lock()` | `Bin` | Make the bin read-only |
| `delete()` | `bool` | Delete the entire bin |
| `fetchQR()` | `QR` | Fetch the PNG QR code (containing bin URL) |
| `update()` | `Bin` | Re-fetch state from the server |

---

## The `File` Object

Represents an individual file.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Filename |
| `bytes` | `int` | File size |
| `content_type` | `str` | MIME type |
| `md5` | `str` | MD5 checksum hash |
| `sha256` | `str` | SHA256 checksum hash |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last updated timestamp |
| `bin` | `Bin` | Parent `Bin` reference |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `download(path)` | `bool` | Download this specific file to a local directory |
| `delete()` | `bool` | Delete this file from the server |

---

## Exceptions

All runtime custom exceptions inherit from the base `FilebinError` class.

| Exception | Detail | HTTP Status |
|-----------|--------|-------------|
| `InvalidBin` | Bin ID not found | `404` |
| `InvalidFile` | File not found in bin | `404` |
| `InvalidBinOrFile` | Upload rejected / File not found | `400 / 404` |
| `InvalidArchiveType` | You tried to download an archive not zip/tar | N/A |
| `DownloadCountReached` | File download limit hit | `403` |
| `StorageFull` | Bin storage limit reached | `403` |
| `LockedBin` | Bin is read-only, upload rejected | `405` |
| `LockFailed` | Lock operation did not take effect | N/A |
