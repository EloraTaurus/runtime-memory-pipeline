# Benchmark Methodology

Runtime Memory Pipeline benchmarks three storage implementations that expose the same runtime recall interface:

- Markdown source files
- SQLite comparison database
- compiled binary runtime fragments

The benchmark is intentionally narrow. It compares storage and loading representations while deliberately sharing the same routing, scoring, relationship following, and context assembly logic across all backends.

## What Is Being Compared

The benchmark compares how the same memory corpus behaves when loaded from:

- human-readable Markdown files
- a SQLite table generated from the Markdown corpus
- versioned binary fragments generated from the Markdown corpus

Each backend returns fragments to the same orchestration layer. That shared layer ranks fragments, follows explicit relationships, applies the context budget, and returns assembled model-facing context.

## What Is Shared

The following are intentionally shared across all benchmark paths:

- source memory content
- fragment metadata
- prompt set
- lexical ranking logic
- relationship traversal logic
- context assembly logic
- token estimate method
- persona and guardrail scoring checks
- contradiction/drift checks

This makes the benchmark a storage representation comparison, not a comparison of three different retrieval algorithms.

## What Is Not Being Compared

This benchmark does not measure:

- language model quality
- model inference latency
- semantic search quality
- embedding generation cost
- vector database performance
- production deployment readiness
- governance correctness
- superiority of binary memory over other approaches

No embeddings or vector databases are used.

## Dataset

The sample dataset is stored in:

```text
sample-artifacts/markdown/
```

It contains small runtime-memory fragments covering:

- runtime identity
- communication style
- guardrail principles
- forbidden claims
- runtime memory principles

The SQLite and binary artifacts are generated from that same Markdown source.

## Benchmark Workflow

The benchmark performs this workflow:

1. Parse the Markdown source corpus.
2. Compile binary fragments and manifest.
3. Build the SQLite comparison database.
4. Measure cold and warm backend load time.
5. Run the same prompts through each backend.
6. Measure retrieval latency.
7. Measure context assembly latency.
8. Measure end-to-end runtime for recall plus assembly.
9. Compute repeated-run variance.
10. Report storage size for each representation.

## Measurements

The structured report includes:

- `build.total_build_time_ms`
- `build.binary_compile_time_ms`
- `load.<backend>.cold_load_ms`
- `load.<backend>.warm_load_ms`
- `retrieval_latency_ms_avg`
- `context_assembly_latency_ms_avg`
- `end_to_end_latency_ms_avg`
- standard deviation for repeated retrieval, assembly, and end-to-end runs
- `storage_bytes`
- persona consistency score
- guardrail adherence score
- drift or contradiction rate
- context token estimate
- fragment count
- RSS delta where available

## Expected Output

Run:

```bash
python3 sample-code/run_benchmark.py
```

The command prints JSON with this top-level shape:

```json
{
  "build": {},
  "load": {},
  "storage_bytes": {},
  "backends": {},
  "summary": [],
  "conclusion": "..."
}
```

Exact timing values vary by machine, OS cache state, Python version, and filesystem. The expected reproducible property is successful execution and a stable report schema, not identical millisecond values.

## Limitations

The default corpus is intentionally small. It is useful for verifying architecture, correctness, and reproducibility, but it is not large enough to prove performance advantage.

The benchmark runs in-process Python code. It does not isolate OS filesystem cache effects, CPU scaling, background load, or interpreter startup costs.

The benchmark currently uses deterministic lexical scoring rather than semantic retrieval. That is intentional: the project is testing a compiled runtime-memory substrate without embeddings.

The benchmark should be interpreted as evidence that the binary backend is valid and comparable on this corpus, not evidence that it is generally faster or better.
