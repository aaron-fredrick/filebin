# Client Reference

The `filebin` package exposes two primary clients:
1. `AsyncFilebinClient` — The native asynchronous client (recommended).
2. `FilebinClient` — A synchronous wrapper.

Both clients expose identical public methods.

::: filebin.client.async_client.AsyncFilebinClient
    options:
      show_root_heading: false
      show_source: false
      members:
        - upload_file
        - download_file
        - delete_file
        - list_bin
        - lock_bin
        - delete_bin
        - download_archive
