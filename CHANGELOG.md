# Changelog

All notable changes to the Runtime Memory Pipeline reference implementation are documented here.

This project is an active research prototype. Version entries describe engineering milestones rather than production releases.

## 2026-07-02 - Engineering Review Tightening And Reproducibility Pass

### Added

* Added `BENCHMARK_METHODOLOGY.md` to document what the benchmark compares, what is shared between backends, expected outputs, and known limitations.
* Added `BENCHMARK_RESULTS_MACBOOK_M4_PRO.md` as an example benchmark run on a MacBook Pro with Apple M4 Pro and 24 GB memory.
* Added lightweight unit tests covering artifact generation and binary validation.
* Added a GitHub Actions workflow to install dependencies, run tests, build artifacts, validate binary output, and execute the benchmark.
* Added `requirements.txt` to make fresh-clone setup explicit. The reference implementation currently uses only the Python standard library.
* Added repository hygiene files and licensing suitable for public review.
* Added changelog coverage for changes made after engineering review.

### Changed

* Expanded benchmark reporting to separate build time, cold load time, warm load time, retrieval latency, context assembly latency, end-to-end runtime, repeated-run variance, and storage footprint.
* Updated the README for clearer public-facing explanation of the research goal, architecture, benchmark scope, reproducibility workflow, and repository layout.
* Added README cross-references from the benchmark section to the methodology document and MacBook Pro benchmark example.
* Regenerated the SQLite sample artifact from the same Markdown corpus used by the Markdown and binary backends.
* Made benchmark output more structured and easier to inspect as a reproducible report.

### Fixed

* Improved binary validation error reporting for magic value, version, CRC, payload checksum, manifest consistency, and fragment relationship checks.
* Ensured validation reports clear failures instead of silently accepting inconsistent binary stores.
* Removed generated local execution artifacts from the repository working tree.

### Notes

* The MacBook Pro benchmark result is included as a reproducibility example, not as a claim that the binary backend is generally faster.
* The latest changes are based on engineering review feedback around reproducibility, benchmark clarity, validation confidence, and repository readability.
* The repository remains intentionally independent from Elora Engine production code.
* A more advanced custom implementation is used in Elora Engine as an active research topic.

## 2026-07-02 - Initial Public Reference Prototype

### Added

* Added a standalone Runtime Memory Pipeline repository structure.
* Added human-readable Markdown source memory under `sample-artifacts/markdown/`.
* Added compiled binary memory artifacts under `sample-artifacts/binary/`.
* Added equivalent SQLite sample data under `sample-artifacts/sqlite/`.
* Added a clean reference implementation under `sample-code/`.
* Added backend implementations for Markdown, SQLite, and compiled binary fragments.
* Added a benchmark harness comparing the three storage approaches using the same corpus and prompts.
* Added README documentation explaining the problem, game-engine asset pipeline inspiration, architecture, benchmark methodology, and research scope.

### Notes

* Markdown remains the editable source of truth.
* Binary fragments are treated as the runtime representation.
* The project does not use embeddings, vector databases, or semantic search.
* The benchmark is designed to compare storage representation and loading path while sharing the same runtime orchestration layer.
