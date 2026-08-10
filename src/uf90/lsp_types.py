from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClientResponse:
    """A JSON-RPC response produced locally instead of forwarded to fortls."""

    message: Mapping[str, Any]
