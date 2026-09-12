"""Every error the engine raises on purpose. `code` is stable; the message may change."""

from __future__ import annotations

from typing import Literal, NoReturn

MaziniErrorCode = Literal[
    "bad_root", "unknown_wazn", "reduced_not_applicable", "unsupported_weakness", "invalid_radicals", "internal"
]


class MaziniError(ValueError):
    code: str

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def internal(message: str) -> NoReturn:
    raise MaziniError("internal", "Internal error: " + message)
