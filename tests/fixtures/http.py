from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class SimpleResponse:
    status_code: int
    body: bytes

    def json(self) -> dict[str, Any]:
        return json.loads(self.body.decode("utf-8"))


class SimpleASGIClient:
    """Minimal HTTP-like test helper without third-party client dependencies."""

    def __init__(self, health_handler: Callable[[], dict[str, str]]) -> None:
        self._health_handler = health_handler

    def get(self, path: str) -> SimpleResponse:
        if path == "/health":
            payload = self._health_handler()
            return SimpleResponse(status_code=200, body=json.dumps(payload).encode("utf-8"))
        return SimpleResponse(status_code=404, body=b'{"detail":"Not Found"}')
