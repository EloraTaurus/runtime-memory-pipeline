# Benchmark Example: MacBook Pro M4 Pro

Date: 2026-07-02

This is an example run of the Runtime Memory Pipeline benchmark on a local Apple Silicon laptop. It is included as a reproducibility example, not as a performance claim.

## Hardware

- Model: MacBook Pro
- Model identifier: Mac16,8
- Chip: Apple M4 Pro
- CPU cores: 12 total, 8 performance and 4 efficiency
- Memory: 24 GB
- macOS: 26.4.1
- Python: 3.13.7

## Dataset

- Markdown files: 3
- Runtime fragments: 5
- Benchmark prompts: 3
- Iterations per prompt/backend: 5
- Context budget: 900 estimated tokens

## Build And Load

| Metric | Result |
| --- | ---: |
| Total build time | 2.028 ms |
| Binary compile time | 0.706 ms |
| Compiled fragments | 0 |
| Skipped unchanged fragments | 5 |

| Backend | Cold load | Warm load | Storage |
| --- | ---: | ---: | ---: |
| Binary | 0.198 ms | 0.151 ms | 6,753 bytes |
| Markdown | 0.225 ms | 0.151 ms | 2,330 bytes |
| SQLite | 0.176 ms | 0.115 ms | 12,288 bytes |

## Summary

| Backend | Avg retrieval | Avg assembly | Avg end-to-end | Std dev | Persona | Guardrails | Drift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Binary | 0.0178 ms | 0.0031 ms | 0.0218 ms | 0.0010 ms | 1.00 | 1.00 | 0.00 |
| Markdown | 0.0210 ms | 0.0038 ms | 0.0263 ms | 0.0059 ms | 1.00 | 1.00 | 0.00 |
| SQLite | 0.0181 ms | 0.0031 ms | 0.0223 ms | 0.0012 ms | 1.00 | 1.00 | 0.00 |

## Interpretation

The binary backend stands up well on this sample corpus:

- binary validation passes
- all five fragments load correctly
- explicit relationships resolve correctly
- persona and guardrail scores match the Markdown and SQLite baselines
- drift/contradiction stays at zero for the sample prompts
- retrieval and context assembly are stable at sub-millisecond scale

This run does not prove that binary memory is faster or generally better. The corpus is intentionally small, and the benchmark shares the same runtime orchestration layer across all backends. The result should be read as evidence that the binary representation is valid, deterministic, and comparable on this machine and dataset.

Larger corpora, cold-start isolation, warm-cache isolation, and additional hardware runs are required before making performance claims.
