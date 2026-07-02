from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .contracts import MemoryFragment

DELIMITER = "<!-- memory-fragment -->"


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in str(value or "").split(",") if part.strip())


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.strip().splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()
    metadata: dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = index + 1
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("\"'")
    return metadata, "\n".join(lines[body_start:]).strip()


def parse_markdown_file(path: Path) -> list[MemoryFragment]:
    source = Path(path)
    chunks = [chunk.strip() for chunk in source.read_text(encoding="utf-8").split(DELIMITER) if chunk.strip()]
    fragments: list[MemoryFragment] = []
    for index, chunk in enumerate(chunks, start=1):
        meta, body = _parse_front_matter(chunk)
        title_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        payload = re.sub(r"^#\s+.+$", "", body, count=1, flags=re.MULTILINE).strip()
        subject = meta.get("subject") or (title_match.group(1) if title_match else source.stem)
        fragment_id = meta.get("id") or f"{source.stem}.{index}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        fragments.append(
            MemoryFragment(
                fragment_id=fragment_id,
                category=meta.get("type", "memory"),
                subject=subject,
                scope=meta.get("scope", "global"),
                timestamp=meta.get("timestamp", ""),
                trust_tier=meta.get("trust_tier", "demo"),
                importance=int(meta.get("importance", "5")),
                relationships=_split_csv(meta.get("relationships", "")),
                tags=_split_csv(meta.get("tags", "")),
                payload=payload,
                source_path=str(source),
                checksum=checksum,
            )
        )
    return fragments


def load_markdown_tree(root: Path) -> list[MemoryFragment]:
    fragments: list[MemoryFragment] = []
    for path in sorted(Path(root).rglob("*.md")):
        fragments.extend(parse_markdown_file(path))
    return fragments
