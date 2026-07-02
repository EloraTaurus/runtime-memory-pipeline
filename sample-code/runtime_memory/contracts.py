from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MemoryFragment:
    fragment_id: str
    category: str
    subject: str
    scope: str
    timestamp: str
    trust_tier: str
    importance: int
    relationships: tuple[str, ...]
    tags: tuple[str, ...]
    payload: str
    source_path: str
    checksum: str


@dataclass(frozen=True)
class RecallResult:
    backend: str
    query: str
    context: str
    latency_ms: float
    retrieval_latency_ms: float
    context_assembly_latency_ms: float
    fragment_count: int
    token_estimate: int


class MemoryBackend(Protocol):
    name: str

    def recall(self, query: str, budget: int = 900) -> RecallResult:
        """Return bounded model-facing context for a query."""
