# HTTP Error Mapping

This table defines the contract for how HTTP status codes returned by Filebin.net are mapped to `filebin` SDK exceptions.

| HTTP Status | Condition | Exception Raised |
|---|---|---|
| 302 | Redirect to S3 | *(Followed automatically)* |
| 400 | Bad upload/invalid bin | `BinNotFoundError` or `FilebinError` |
| 403 | Storage full | `StorageFullError` |
| 403 | Download limit reached | `AuthenticationError` |
| 403 | Bin not approved | `AuthenticationError` |
| 404 | Bin not found | `BinNotFoundError` |
| 404 | File not found | `FileNotFoundError` |
| 404 | Upload to locked bin | `BinNotFoundError` (or generic locked) |
| 429 | Rate limited | `RateLimitError` |
| 500-599 | Server errors | `ServerError` |
| (network) | aiohttp timeout | `TimeoutError` |
| (network) | aiohttp client error| `NetworkError` |

*Note: The `HttpTransport` class in `filebin/core/http.py` is the absolute source of truth for these mappings.*
