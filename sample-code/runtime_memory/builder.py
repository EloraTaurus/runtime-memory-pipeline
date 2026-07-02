from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
from dataclasses import replace
from pathlib import Path

from .binary_format import VERSION, fragment_to_bytes
from .contracts import MemoryFragment
from .markdown_parser import load_markdown_tree


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "fragment"


def compile_binary(fragments: list[MemoryFragment], binary_root: Path) -> dict[str, object]:
    binary_root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    compiled = 0
    skipped = 0
    started = time.perf_counter()
    for fragment in fragments:
        relative = Path(fragment.scope) / f"{_safe_name(fragment.fragment_id)}.bin"
        target = binary_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = fragment_to_bytes(fragment)
        if target.exists() and target.read_bytes() == data:
            skipped += 1
        else:
            target.write_bytes(data)
            compiled += 1
        entries.append(
            {
                "id": fragment.fragment_id,
                "path": relative.as_posix(),
                "category": fragment.category,
                "scope": fragment.scope,
                "subject": fragment.subject,
                "trust_tier": fragment.trust_tier,
                "importance": fragment.importance,
                "relationships": list(fragment.relationships),
                "tags": list(fragment.tags),
                "checksum": fragment.checksum,
            }
        )
    manifest = {
        "format": "runtime-memory-pipeline",
        "version": VERSION,
        "compiled_at": 0,
        "compile_time_ms": 0.0,
        "fragment_count": len(entries),
        "compiled_count": compiled,
        "skipped_unchanged_count": skipped,
        "fragments": entries,
    }
    (binary_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    result = dict(manifest)
    result["compiled_at"] = int(time.time())
    result["compile_time_ms"] = (time.perf_counter() - started) * 1000
    return result


def build_sqlite(fragments: list[MemoryFragment], sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runtime_memory (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            scope TEXT NOT NULL,
            subject TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            trust_tier TEXT NOT NULL,
            importance INTEGER NOT NULL,
            relationships_json TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            payload TEXT NOT NULL,
            source_path TEXT NOT NULL,
            checksum TEXT NOT NULL
        )
        """
    )
    conn.execute("DELETE FROM runtime_memory")
    conn.executemany(
        "INSERT INTO runtime_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                fragment.fragment_id,
                fragment.category,
                fragment.scope,
                fragment.subject,
                fragment.timestamp,
                fragment.trust_tier,
                fragment.importance,
                json.dumps(list(fragment.relationships), sort_keys=True),
                json.dumps(list(fragment.tags), sort_keys=True),
                fragment.payload,
                fragment.source_path,
                fragment.checksum,
            )
            for fragment in fragments
        ],
    )
    conn.commit()
    conn.close()


def build(markdown_root: Path, binary_root: Path, sqlite_path: Path) -> dict[str, object]:
    source_root = Path(markdown_root)
    fragments = [
        replace(fragment, source_path=Path(fragment.source_path).relative_to(source_root).as_posix())
        for fragment in load_markdown_tree(source_root)
    ]
    manifest = compile_binary(fragments, binary_root)
    build_sqlite(fragments, sqlite_path)
    return {"manifest": manifest, "sqlite": str(sqlite_path), "markdown": str(markdown_root)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build runtime memory sample artifacts.")
    parser.add_argument("--markdown", default="sample-artifacts/markdown")
    parser.add_argument("--binary", default="sample-artifacts/binary")
    parser.add_argument("--sqlite", default="sample-artifacts/sqlite/runtime_memory.sqlite3")
    args = parser.parse_args()
    result = build(Path(args.markdown), Path(args.binary), Path(args.sqlite))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
