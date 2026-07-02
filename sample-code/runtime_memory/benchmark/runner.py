from __future__ import annotations

import statistics
import time
from pathlib import Path

from ..backends import BinaryBackend, MarkdownBackend, SQLiteBackend
from ..builder import build
from .metrics import contradiction_rate, rss_mb, storage_size, term_score

ROOT = Path(__file__).resolve().parents[3]
MARKDOWN = ROOT / "sample-artifacts" / "markdown"
BINARY = ROOT / "sample-artifacts" / "binary"
SQLITE = ROOT / "sample-artifacts" / "sqlite" / "runtime_memory.sqlite3"

PROMPTS = (
    {
        "id": "identity",
        "query": "How should the runtime describe its identity?",
        "expected": ("local", "prototype", "experimental"),
        "guardrail": (),
        "forbidden": ("should claim sentience", "has proven superiority"),
    },
    {
        "id": "guardrails",
        "query": "What guardrails and forbidden claims apply?",
        "expected": ("guardrails", "auditable", "operator"),
        "guardrail": ("bounded", "evidence", "benchmark"),
        "forbidden": ("should claim binary memory is faster without benchmark evidence",),
    },
    {
        "id": "runtime",
        "query": "How does the binary runtime memory pipeline work?",
        "expected": ("markdown", "binary", "runtime"),
        "guardrail": (),
        "forbidden": ("vector database",),
    },
)


def run(iterations: int = 5, budget: int = 900) -> dict[str, object]:
    build(MARKDOWN, BINARY, SQLITE)
    backends = {
        "markdown": MarkdownBackend(MARKDOWN),
        "sqlite": SQLiteBackend(SQLITE),
        "binary": BinaryBackend(BINARY),
    }
    results: dict[str, object] = {
        "iterations": iterations,
        "budget": budget,
        "storage_bytes": {
            "markdown": storage_size(MARKDOWN),
            "sqlite": storage_size(SQLITE),
            "binary": storage_size(BINARY),
        },
        "backends": {},
        "summary": [],
        "conclusion": (
            "Binary backend is functioning and deterministic on this sample corpus. "
            "No superiority claim is made; larger cold-start and warm-cache benchmarks are required."
        ),
    }
    summary_rows: list[dict[str, object]] = []
    for name, backend in backends.items():
        rows = []
        for prompt in PROMPTS:
            latencies = []
            contexts = []
            start_rss = rss_mb()
            started = time.perf_counter()
            recall = None
            for _ in range(iterations):
                recall = backend.recall(prompt["query"], budget=budget)
                latencies.append(recall.latency_ms)
                contexts.append(recall.context)
            assert recall is not None
            context = contexts[-1]
            rows.append(
                {
                    "prompt_id": prompt["id"],
                    "retrieval_latency_ms_avg": statistics.fmean(latencies),
                    "end_to_end_latency_ms_avg": ((time.perf_counter() - started) * 1000) / iterations,
                    "persona_consistency": term_score(context, prompt["expected"]),
                    "guardrail_adherence": term_score(context, prompt["guardrail"]),
                    "drift_or_contradiction_rate": contradiction_rate(context, prompt["forbidden"]),
                    "context_token_estimate": recall.token_estimate,
                    "fragment_count": recall.fragment_count,
                    "rss_mb_delta": max(0.0, rss_mb() - start_rss),
                }
            )
        results["backends"][name] = rows
        summary_rows.append(
            {
                "backend": name,
                "avg_retrieval_ms": statistics.fmean(row["retrieval_latency_ms_avg"] for row in rows),
                "avg_end_to_end_ms": statistics.fmean(row["end_to_end_latency_ms_avg"] for row in rows),
                "avg_persona": statistics.fmean(row["persona_consistency"] for row in rows),
                "avg_guardrails": statistics.fmean(row["guardrail_adherence"] for row in rows),
                "avg_drift": statistics.fmean(row["drift_or_contradiction_rate"] for row in rows),
                "storage_bytes": results["storage_bytes"][name],
            }
        )
    results["summary"] = sorted(summary_rows, key=lambda row: str(row["backend"]))
    return results
