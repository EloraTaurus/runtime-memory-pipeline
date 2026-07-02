from __future__ import annotations

import statistics
import time
from pathlib import Path

from ..backends import BinaryBackend, MarkdownBackend, SQLiteBackend
from ..builder import build
from .metrics import contradiction_rate, rss_mb, storage_size, term_score, variance

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
    build_started = time.perf_counter()
    build_result = build(MARKDOWN, BINARY, SQLITE)
    build_time_ms = (time.perf_counter() - build_started) * 1000
    cold_load_times: dict[str, float] = {}
    warm_load_times: dict[str, float] = {}
    backend_factories = {
        "markdown": lambda: MarkdownBackend(MARKDOWN),
        "sqlite": lambda: SQLiteBackend(SQLITE),
        "binary": lambda: BinaryBackend(BINARY),
    }
    for name, factory in backend_factories.items():
        started = time.perf_counter()
        factory()
        cold_load_times[name] = (time.perf_counter() - started) * 1000
        started = time.perf_counter()
        factory()
        warm_load_times[name] = (time.perf_counter() - started) * 1000
    backends = {
        name: factory()
        for name, factory in backend_factories.items()
    }
    results: dict[str, object] = {
        "iterations": iterations,
        "budget": budget,
        "build": {
            "total_build_time_ms": build_time_ms,
            "binary_compile_time_ms": build_result["manifest"]["compile_time_ms"],
            "compiled_count": build_result["manifest"]["compiled_count"],
            "skipped_unchanged_count": build_result["manifest"]["skipped_unchanged_count"],
            "fragment_count": build_result["manifest"]["fragment_count"],
        },
        "load": {
            name: {
                "cold_load_ms": cold_load_times[name],
                "warm_load_ms": warm_load_times[name],
            }
            for name in sorted(backends)
        },
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
            retrieval_latencies = []
            assembly_latencies = []
            end_to_end_latencies = []
            contexts = []
            start_rss = rss_mb()
            recall = None
            for _ in range(iterations):
                started = time.perf_counter()
                recall = backend.recall(prompt["query"], budget=budget)
                end_to_end_latencies.append((time.perf_counter() - started) * 1000)
                retrieval_latencies.append(recall.retrieval_latency_ms)
                assembly_latencies.append(recall.context_assembly_latency_ms)
                contexts.append(recall.context)
            assert recall is not None
            context = contexts[-1]
            rows.append(
                {
                    "prompt_id": prompt["id"],
                    "retrieval_latency_ms_avg": statistics.fmean(retrieval_latencies),
                    "context_assembly_latency_ms_avg": statistics.fmean(assembly_latencies),
                    "end_to_end_latency_ms_avg": statistics.fmean(end_to_end_latencies),
                    "retrieval_latency_ms_stddev": variance(retrieval_latencies),
                    "context_assembly_latency_ms_stddev": variance(assembly_latencies),
                    "end_to_end_latency_ms_stddev": variance(end_to_end_latencies),
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
                "avg_context_assembly_ms": statistics.fmean(row["context_assembly_latency_ms_avg"] for row in rows),
                "avg_end_to_end_ms": statistics.fmean(row["end_to_end_latency_ms_avg"] for row in rows),
                "avg_end_to_end_stddev_ms": statistics.fmean(row["end_to_end_latency_ms_stddev"] for row in rows),
                "cold_load_ms": cold_load_times[name],
                "warm_load_ms": warm_load_times[name],
                "avg_persona": statistics.fmean(row["persona_consistency"] for row in rows),
                "avg_guardrails": statistics.fmean(row["guardrail_adherence"] for row in rows),
                "avg_drift": statistics.fmean(row["drift_or_contradiction_rate"] for row in rows),
                "storage_bytes": results["storage_bytes"][name],
            }
        )
    results["summary"] = sorted(summary_rows, key=lambda row: str(row["backend"]))
    return results
