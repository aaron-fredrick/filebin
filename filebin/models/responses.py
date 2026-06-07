"""Typed response shapes from the Filebin API.

Since the primary response structures are purely bins and files,
this module serves mostly to re-export or alias complex structural types
if the API evolves to return paginated lists or wrapper envelopes.

Currently, the API returns raw JSON dicts that map cleanly 1:1 to BinModel and FileModel.
"""

from typing import Any

# For now, we type-alias the raw API dict shapes to clarify intent in the client.
BinResponse = dict[str, Any]
FileUploadResponse = dict[str, Any]
