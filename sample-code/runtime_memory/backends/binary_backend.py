from __future__ import annotations

import json
from pathlib import Path

from ..binary_format import fragment_from_bytes
from ..validation import validate_binary_store
from .common import FragmentBackend


class BinaryBackend(FragmentBackend):
    name = "binary"

    def __init__(self, binary_root: Path) -> None:
        root = Path(binary_root)
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        fragments = [fragment_from_bytes((root / row["path"]).read_bytes()) for row in manifest["fragments"]]
        super().__init__(fragments)


def validate(binary_root: Path) -> dict[str, object]:
    result = validate_binary_store(binary_root)
    if result["ok"]:
        result["root"] = str(binary_root)
    return result
