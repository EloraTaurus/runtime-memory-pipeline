from __future__ import annotations

import time

from ..contracts import MemoryFragment, RecallResult


def tokens(text: str) -> set[str]:
    return {part.strip(".,:;!?()[]").lower() for part in text.split() if part.strip(".,:;!?()[]")}


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.25)) if text.strip() else 0


def score(fragment: MemoryFragment, query: str) -> float:
    query_tokens = tokens(query)
    haystack = " ".join([fragment.category, fragment.subject, " ".join(fragment.tags), fragment.payload])
    overlap = len(query_tokens & tokens(haystack))
    return overlap + (fragment.importance / 10.0)


def assemble(fragments: list[MemoryFragment], budget: int) -> tuple[str, int]:
    parts: list[str] = []
    used = 0
    for fragment in fragments:
        block = f"[{fragment.category}:{fragment.subject}]\n{fragment.payload}"
        size = estimate_tokens(block)
        if parts and used + size > budget:
            continue
        parts.append(block)
        used += size
        if used >= budget:
            break
    return "\n\n".join(parts), used


class FragmentBackend:
    name = "fragment"

    def __init__(self, fragments: list[MemoryFragment]) -> None:
        self.fragments = fragments
        self.by_id = {fragment.fragment_id: fragment for fragment in fragments}

    def retrieve(self, query: str) -> list[MemoryFragment]:
        ranked = sorted(self.fragments, key=lambda item: (-score(item, query), -item.importance, item.fragment_id))
        selected: list[MemoryFragment] = []
        seen: set[str] = set()
        for fragment in ranked:
            if fragment.fragment_id in seen:
                continue
            selected.append(fragment)
            seen.add(fragment.fragment_id)
            for related_id in fragment.relationships:
                related = self.by_id.get(related_id)
                if related and related.fragment_id not in seen:
                    selected.append(related)
                    seen.add(related.fragment_id)
        return selected

    def recall(self, query: str, budget: int = 900) -> RecallResult:
        started = time.perf_counter()
        retrieval_started = time.perf_counter()
        selected = self.retrieve(query)
        retrieval_ms = (time.perf_counter() - retrieval_started) * 1000
        assembly_started = time.perf_counter()
        context, token_count = assemble(selected, budget)
        assembly_ms = (time.perf_counter() - assembly_started) * 1000
        total_ms = (time.perf_counter() - started) * 1000
        return RecallResult(
            backend=self.name,
            query=query,
            context=context,
            latency_ms=total_ms,
            retrieval_latency_ms=retrieval_ms,
            context_assembly_latency_ms=assembly_ms,
            fragment_count=len(selected),
            token_estimate=token_count,
        )
