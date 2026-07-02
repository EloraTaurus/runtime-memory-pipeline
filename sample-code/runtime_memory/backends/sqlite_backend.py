from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..contracts import MemoryFragment
from .common import FragmentBackend


class SQLiteBackend(FragmentBackend):
    name = "sqlite"

    def __init__(self, sqlite_path: Path) -> None:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM runtime_memory ORDER BY id").fetchall()
        conn.close()
        fragments = [
            MemoryFragment(
                fragment_id=row["id"],
                category=row["category"],
                subject=row["subject"],
                scope=row["scope"],
                timestamp=row["timestamp"],
                trust_tier=row["trust_tier"],
                importance=int(row["importance"]),
                relationships=tuple(json.loads(row["relationships_json"])),
                tags=tuple(json.loads(row["tags_json"])),
                payload=row["payload"],
                source_path=row["source_path"],
                checksum=row["checksum"],
            )
            for row in rows
        ]
        super().__init__(fragments)
