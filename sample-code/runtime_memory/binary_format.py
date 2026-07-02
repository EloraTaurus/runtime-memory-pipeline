from __future__ import annotations

import hashlib
import json
import struct
import zlib
from dataclasses import asdict

from .contracts import MemoryFragment

MAGIC = b"RMP1"
VERSION = 1
HEADER = struct.Struct("<4sHIII")


def fragment_to_bytes(fragment: MemoryFragment) -> bytes:
    payload = fragment.payload.encode("utf-8")
    metadata = asdict(fragment)
    metadata["relationships"] = list(fragment.relationships)
    metadata["tags"] = list(fragment.tags)
    header = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    crc = zlib.crc32(header + payload) & 0xFFFFFFFF
    return HEADER.pack(MAGIC, VERSION, len(header), len(payload), crc) + header + payload


def fragment_from_bytes(data: bytes) -> MemoryFragment:
    if len(data) < HEADER.size:
        raise ValueError("binary fragment is shorter than fixed header")
    magic, version, header_len, payload_len, expected_crc = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise ValueError(f"invalid magic: expected {MAGIC!r}, got {magic!r}")
    if version != VERSION:
        raise ValueError(f"unsupported version: expected {VERSION}, got {version}")
    expected_len = HEADER.size + header_len + payload_len
    if len(data) != expected_len:
        raise ValueError(f"length mismatch: expected {expected_len} bytes, got {len(data)}")
    header = data[HEADER.size : HEADER.size + header_len]
    payload = data[HEADER.size + header_len :]
    actual_crc = zlib.crc32(header + payload) & 0xFFFFFFFF
    if actual_crc != expected_crc:
        raise ValueError(f"crc mismatch: expected {expected_crc}, got {actual_crc}")
    meta = json.loads(header.decode("utf-8"))
    checksum = hashlib.sha256(payload).hexdigest()
    if checksum != meta["checksum"]:
        raise ValueError(f"payload checksum mismatch for {meta.get('fragment_id', '<unknown>')}")
    return MemoryFragment(
        fragment_id=meta["fragment_id"],
        category=meta["category"],
        subject=meta["subject"],
        scope=meta["scope"],
        timestamp=meta["timestamp"],
        trust_tier=meta["trust_tier"],
        importance=int(meta["importance"]),
        relationships=tuple(meta["relationships"]),
        tags=tuple(meta["tags"]),
        payload=payload.decode("utf-8"),
        source_path=meta["source_path"],
        checksum=checksum,
    )
