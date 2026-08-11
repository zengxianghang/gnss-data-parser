"""Streaming text input helpers."""

from __future__ import annotations

from contextlib import contextmanager
from os import PathLike
from typing import Iterator, TextIO, TypeAlias

TextSource: TypeAlias = str | PathLike[str] | TextIO


@contextmanager
def open_text_source(
    source: TextSource,
    *,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[TextIO]:
    """Yield a readable text stream for a path or an existing text stream.

    Streams supplied by the caller are never closed here. Streams opened from
    paths are closed automatically.
    """
    if hasattr(source, "read"):
        yield source  # type: ignore[misc]
        return

    with open(source, "r", encoding=encoding, errors=errors, newline="") as stream:
        yield stream


def iter_text_lines(
    source: TextSource,
    *,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[tuple[int, str]]:
    """Yield ``(1-based line number, line text)`` without loading the file.

    Newline characters are removed, while other leading/trailing whitespace is
    preserved because vendor formats may depend on exact field layout.
    """
    with open_text_source(source, encoding=encoding, errors=errors) as stream:
        for line_number, line in enumerate(stream, start=1):
            yield line_number, line.rstrip("\r\n")
