from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .binary_format import fragment_from_bytes


def validate_binary_store(binary_root: Path) -> dict[str, Any]:
    root = Path(binary_root)
    manifest_path = root / "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    fragments_by_id: dict[str, object] = {}

    if not manifest_path.exists():
        return {
            "ok": False,
            "errors": [f"manifest not found: {manifest_path}"],
            "warnings": [],
            "fragment_count": 0,
            "validated_count": 0,
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "errors": [f"manifest is not valid JSON: {exc}"],
            "warnings": [],
            "fragment_count": 0,
            "validated_count": 0,
        }

    if manifest.get("format") != "runtime-memory-pipeline":
        errors.append("manifest format mismatch")
    if int(manifest.get("version") or 0) != 1:
        errors.append(f"manifest version mismatch: {manifest.get('version')!r}")

    manifest_rows = manifest.get("fragments")
    if not isinstance(manifest_rows, list):
        errors.append("manifest fragments must be a list")
        manifest_rows = []

    seen_ids: set[str] = set()
    validated = 0
    for index, row in enumerate(manifest_rows):
        if not isinstance(row, dict):
            errors.append(f"manifest fragment row {index} is not an object")
            continue
        fragment_id = str(row.get("id") or "")
        rel_path = str(row.get("path") or "")
        if not fragment_id:
            errors.append(f"manifest fragment row {index} is missing id")
            continue
        if fragment_id in seen_ids:
            errors.append(f"duplicate manifest fragment id: {fragment_id}")
        seen_ids.add(fragment_id)
        if not rel_path:
            errors.append(f"manifest fragment {fragment_id} is missing path")
            continue
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing binary fragment for {fragment_id}: {rel_path}")
            continue
        try:
            fragment = fragment_from_bytes(path.read_bytes())
        except Exception as exc:
            errors.append(f"invalid binary fragment {rel_path}: {exc}")
            continue
        if fragment.fragment_id != fragment_id:
            errors.append(f"manifest id mismatch for {rel_path}: manifest={fragment_id}, binary={fragment.fragment_id}")
        if row.get("checksum") and row["checksum"] != fragment.checksum:
            errors.append(f"payload checksum mismatch for {fragment_id}")
        if row.get("scope") and row["scope"] != fragment.scope:
            errors.append(f"scope mismatch for {fragment_id}")
        if row.get("category") and row["category"] != fragment.category:
            errors.append(f"category mismatch for {fragment_id}")
        fragments_by_id[fragment.fragment_id] = fragment
        validated += 1

    for fragment in fragments_by_id.values():
        for related_id in getattr(fragment, "relationships", ()):
            if related_id not in fragments_by_id:
                errors.append(f"missing related fragment: {fragment.fragment_id} -> {related_id}")

    binary_files = sorted(root.rglob("*.bin"))
    manifest_paths = {str(row.get("path") or "") for row in manifest_rows if isinstance(row, dict)}
    for path in binary_files:
        rel = path.relative_to(root).as_posix()
        if rel not in manifest_paths:
            warnings.append(f"binary fragment is not listed in manifest: {rel}")

    expected_count = int(manifest.get("fragment_count") or len(manifest_rows))
    if expected_count != len(manifest_rows):
        errors.append(f"manifest fragment_count mismatch: expected {expected_count}, rows={len(manifest_rows)}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "fragment_count": len(manifest_rows),
        "validated_count": validated,
        "manifest_path": str(manifest_path),
    }
