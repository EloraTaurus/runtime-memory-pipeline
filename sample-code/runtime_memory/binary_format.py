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
        raise ValueError("invalid magic")
    if version != VERSION:
        raise ValueError(f"unsupported version: {version}")
    expected_len = HEADER.size + header_len + payload_len
    if len(data) != expected_len:
        raise ValueError("length mismatch")
    header = data[HEADER.size : HEADER.size + header_len]
    payload = data[HEADER.size + header_len :]
    if (zlib.crc32(header + payload) & 0xFFFFFFFF) != expected_crc:
        raise ValueError("crc mismatch")
    meta = json.loads(header.decode("utf-8"))
    checksum = hashlib.sha256(payload).hexdigest()
    if checksum != meta["checksum"]:
        raise ValueError("payload checksum mismatch")
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
