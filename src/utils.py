# src/utils.py
import re

class TitleNotFoundError(RuntimeError):
    """Raised when a markdown document does not contain an H1 title."""
    pass


def extract_title(markdown: str) -> str:
    """
    Return the text of the first level‑1 heading (a line that starts with a single '#').

    The leading ``#`` and any surrounding whitespace are stripped.
    If no such heading exists, a :class:`TitleNotFoundError` is raised.

    Example
    -------
    >>> extract_title("# Hello")
    'Hello'
    """
    # Split into lines to avoid matching headings that are part of a code block.
    for line in markdown.splitlines():
        # Strip leading spaces then check for exactly one '#'
        stripped = line.lstrip()
        if stripped.startswith("# "):
            # remove the leading '#', then strip surrounding whitespace
            return stripped[1:].strip()
        # Accept a pure "#" without a trailing space (e.g. "#Title")
        if stripped.startswith("#") and not stripped.startswith("##"):
            return stripped[1:].strip()
    raise TitleNotFoundError("No top‑level (H1) heading found in markdown.")