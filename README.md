# Runtime Memory Pipeline

**Status:** Active Research Prototype

Runtime Memory Pipeline is a research project exploring whether techniques traditionally used by classic game engines can be adapted to AI runtime memory.

Modern AI memory systems commonly rely on Markdown documents, relational databases such as SQLite, or vector databases backed by embedding search. While these approaches are well established, they also introduce runtime costs such as document parsing, database queries, embedding generation, semantic indexing, or additional retrieval layers before useful context can be assembled.

This project investigates an alternative architecture.

Instead of treating AI memory as documents or vectors, Runtime Memory Pipeline treats memory as a compiled runtime asset. Human-readable knowledge is compiled into compact binary fragments which are streamed, routed, and assembled by a lightweight runtime orchestrator before being supplied to a language model.

The project draws inspiration from the compiled asset pipelines used by game engines throughout the 1990s and early 2000s, where constrained hardware encouraged deterministic loading, efficient resource management, and predictable runtime behaviour.

This repository is intentionally independent from production systems. It serves as a public engineering reference, benchmark, and research implementation that other builders can inspect, reproduce, extend, or benchmark against.

A more advanced implementation of these ideas is currently being researched within **The Elora Taurus Project (Elora Engine)**.

---

# Live Research

Runtime Memory Pipeline represents the reference implementation of an active research topic.

The production implementation continues to evolve inside **The Elora Taurus Project (Elora Engine)** as part of ongoing work into CPU-first AI runtime architecture, deterministic memory orchestration, and governed AI systems.

This repository intentionally remains independent so that the concepts can be evaluated without requiring the wider Elora Engine.

**Project Website**

https://elorataurus.com/

**Live Engine**

https://ai.elorataurus.com/

---

# Research Disclaimer

This repository explores one possible runtime memory architecture.

Its purpose is to encourage reproducible engineering experiments rather than demonstrate a universally superior solution.

Performance characteristics should always be validated through repeatable benchmarking using identical datasets and workloads.

---

# The Problem

Most AI memory systems today begin with one of three approaches:

* Markdown or text documents
* SQLite or other relational databases
* Vector databases using embeddings

Each approach provides useful capabilities, but they also introduce runtime work before useful context reaches the language model.

Examples include:

* document parsing
* SQL query execution
* embedding generation
* semantic indexing
* similarity search
* additional retrieval orchestration

For many workloads this overhead is entirely reasonable.

However, some categories of AI memory are fundamentally deterministic.

Identity.

Persona.

Guardrails.

Runtime policy.

Operator preferences.

Session state.

These are often better described as structured runtime assets than fuzzy semantic knowledge.

This project investigates whether those categories can be managed more efficiently using compiled binary fragments inspired by classic game-engine asset pipelines.

---

# Research Question

**Can a compiled binary memory system inspired by classic game-engine asset streaming provide a deterministic, CPU-friendly alternative to traditional AI memory implementations?**

---

# Core Hypothesis

The central hypothesis is that AI runtime memory can be treated as a compiled runtime asset rather than a document or database.

Instead of repeatedly parsing authoring formats during execution, human-readable knowledge is compiled once into binary runtime artifacts.

At runtime, a lightweight orchestrator streams only the required fragments, assembles deterministic context, and supplies it to the language model.

---

# Architecture

```text
Markdown Knowledge
        │
        ▼
Runtime Memory Builder
        │
        ▼
Compiled Binary Memory
        │
        ▼
Runtime Memory Orchestrator
        │
        ▼
Context Assembly
        │
        ▼
Language Model
```

Markdown remains the editable source of truth.

Binary memory becomes the runtime representation.

---

# Runtime Retrieval

Unlike document parsing or SQL-backed retrieval, the Runtime Memory Pipeline performs deterministic fragment assembly.

```text
Prompt
        │
        ▼
Memory Router
        │
        ▼
Scope Selection
        │
        ▼
Binary Fragment Header Scan
        │
        ▼
Relationship Resolution
        │
        ▼
Budgeted Context Assembly
        │
        ▼
Language Model
```

The runtime does not repeatedly parse Markdown documents.

The runtime does not perform SQL queries.

The runtime does not require embedding generation or vector similarity search.

Instead, it loads compact binary fragment headers, identifies relevant fragments through deterministic routing, follows explicit relationships, and assembles bounded runtime context.

---

# Binary Fragment Format

The prototype binary format is intentionally compact and inspectable.

Each fragment contains:

* 4-byte magic (`RMP1`)
* version identifier
* metadata length
* payload length
* CRC32 integrity verification
* JSON metadata header
* UTF-8 payload

Metadata currently includes:

* fragment identifier
* category
* subject
* trust tier
* importance
* tags
* relationships
* source path
* payload checksum

This format is intended as a research prototype rather than a finalized specification.

---

# Benchmark Methodology

The benchmark evaluates identical memory across three backends:

* Markdown
* SQLite
* Binary Runtime Memory

Measurements include:

* retrieval latency
* context assembly latency
* end-to-end response latency
* persona consistency
* guardrail adherence
* contradiction and drift
* context size
* CPU utilisation
* RAM utilisation
* storage footprint

The benchmark does **not** attempt to prove that binary memory is superior.

Its purpose is to provide a reproducible framework for comparing different runtime memory architectures under identical conditions.

---

# Repository Layout

```text
Runtime-Memory-Pipeline/

README.md

sample-code/

sample-artifacts/
```

---

# Quick Start

Run the benchmark:

```bash
cd Runtime-Memory-Pipeline
python3 sample-code/run_benchmark.py
```

Rebuild runtime artifacts:

```bash
python3 sample-code/build_artifacts.py
```

Validate binary fragments:

```bash
python3 sample-code/binary_backend.py
```

---

# Non-Goals

* Replace existing AI memory systems.
* Replace vector databases.
* Replace relational databases.
* Demonstrate universal superiority.
* Depend on production Elora Engine code.

---

# Current Status

Current implementation includes:

* Markdown authoring format
* Runtime Memory Builder
* Versioned binary fragment format
* SQLite comparison backend
* Binary comparison backend
* Benchmark harness
* Reference implementation suitable for experimentation

---

# Community

This repository is intended as an engineering reference rather than a finished framework.

If you build your own implementation, improve the binary format, experiment with alternative routing strategies, or benchmark different runtime memory architectures, I'd genuinely be interested in seeing the results.

Independent experimentation and reproducible comparisons are encouraged.

---

# Why Build This?

The purpose of this project is not to replace existing AI memory techniques.

Instead, it explores whether decades of engineering experience from game engines can provide useful ideas for AI runtime infrastructure.

Even if the binary approach ultimately proves no faster than existing techniques, the benchmark itself contributes useful engineering evidence by comparing multiple runtime memory architectures under identical conditions.

---

# License

This repository is licensed under the Apache License 2.0.

The goal is to encourage experimentation, commercial and non-commercial use, independent benchmarking, and alternative implementations while preserving the openness of shared contributions through Apache's patent provisions.

This repository is licensed independently from **The Elora Taurus Project**.

See the accompanying `LICENSE` file for the complete license.

---

# Summary

Runtime Memory Pipeline explores whether AI memory can be treated as a compiled runtime asset rather than a document or database.

By applying ideas from classic game-engine asset streaming to AI runtime infrastructure, the project aims to provide a reproducible research platform for evaluating deterministic, CPU-first memory architectures.
