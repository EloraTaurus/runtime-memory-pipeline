from __future__ import annotations

from pathlib import Path

from ..markdown_parser import load_markdown_tree
from .common import FragmentBackend


class MarkdownBackend(FragmentBackend):
    name = "markdown"

    def __init__(self, markdown_root: Path) -> None:
        super().__init__(load_markdown_tree(markdown_root))
