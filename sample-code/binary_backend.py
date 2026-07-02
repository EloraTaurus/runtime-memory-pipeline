from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime_memory.backends.binary_backend import BinaryBackend, validate


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sample-artifacts/binary")
    result = validate(root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
