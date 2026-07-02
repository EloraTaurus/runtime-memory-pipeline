from __future__ import annotations

from runtime_memory.binary_format import fragment_from_bytes, fragment_to_bytes
from runtime_memory.builder import build, build_sqlite, compile_binary, main
from runtime_memory.contracts import MemoryFragment
from runtime_memory.markdown_parser import load_markdown_tree, parse_markdown_file


if __name__ == "__main__":
    raise SystemExit(main())
