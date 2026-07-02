from __future__ import annotations

import resource
from pathlib import Path
from statistics import pstdev


def rss_mb() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def term_score(context: str, terms: tuple[str, ...]) -> float:
    if not terms:
        return 1.0
    lower = context.lower()
    return sum(1 for term in terms if term.lower() in lower) / len(terms)


def contradiction_rate(context: str, terms: tuple[str, ...]) -> float:
    if not terms:
        return 0.0
    lower = context.lower()
    return sum(1 for term in terms if term.lower() in lower) / len(terms)


def storage_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return pstdev(values)
