"""ANSI color formatting for output in terminal."""

from __future__ import annotations

from modules.thirdparty.termcolor.termcolor import ATTRIBUTES, COLORS, HIGHLIGHTS, RESET, colored, cprint

__all__ = [
    "ATTRIBUTES",
    "COLORS",
    "HIGHLIGHTS",
    "RESET",
    "colored",
    "cprint",
]
