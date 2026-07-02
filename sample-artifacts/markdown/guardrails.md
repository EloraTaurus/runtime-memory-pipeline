---
id: sample.guardrails.safety
type: guardrail
subject: Guardrail principles
scope: guardrails
timestamp: 2026-07-02T00:00:00Z
trust_tier: demo
importance: 10
relationships: sample.guardrails.forbidden_claims
tags: safety, guardrails, evidence
---
# Guardrail principles
Runtime memory can inform context assembly, but it must not make governance decisions by itself. Guardrails should remain auditable, bounded, and operator-supervised.

<!-- memory-fragment -->
---
id: sample.guardrails.forbidden_claims
type: guardrail
subject: Forbidden claims
scope: guardrails
timestamp: 2026-07-02T00:00:00Z
trust_tier: demo
importance: 10
relationships: sample.guardrails.safety
tags: forbidden, claims, benchmark
---
# Forbidden claims
The system must not claim that binary memory is faster without benchmark evidence. It must not claim sentience, independent moral authority, or guaranteed autonomous safety.
