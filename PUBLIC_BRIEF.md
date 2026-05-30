# AIntegrity — Public Brief

**Author:** Steven Dark | Independent AI Safety Researcher | Aberdeen, Scotland

---

## Problem

Epistemic decay in AI systems — LLMs that contradict themselves, evade questioning, and drift semantically over time. Current alignment approaches assume the model's context is reliable; AIntegrity detects when that assumption fails.

The core failure mode is not malice but epistemic corruption: a model that has been manipulated through prompt injection, context poisoning, or accumulated conversational drift will produce outputs that are internally consistent but factually or logically compromised. Standard alignment techniques (RLHF, constitutional AI, guardrails) operate on the assumption that the model's context window contains trustworthy information. When that assumption is violated, alignment faithfully pursues a corrupted goal.

---

## Thesis

> "Alignment presupposes epistemology. A perfectly aligned system operating on corrupted context will faithfully pursue a corrupted goal."

Alignment without epistemic verification is necessary but insufficient. AIntegrity provides the epistemic layer that alignment frameworks assume but do not verify.

---

## Approach

### PLI — Persistent Logical Interrogation

A five-state interrogation cycle designed to detect behavioral inconsistency in LLM systems:

| State | Function |
|-------|----------|
| **CONFRONT** | Present the model with a claim derived from its own prior outputs |
| **DETECT** | Monitor for contradiction, evasion, or semantic drift in the response |
| **COUNTER** | Challenge detected inconsistencies with structured follow-up probes |
| **ESCALATE** | Increase interrogation pressure on confirmed failure patterns |
| **FORCE** | Demand explicit resolution — the model must commit to a position or acknowledge uncertainty |

PLI identifies nine categorised failure modes across the interrogation cycle, covering contradiction, evasion, hedging, false confidence, and semantic shifting.

---

## Key Components

### PLI Engine
Three-layer analysis pipeline:
1. **Regex pattern matching** — fast detection of known evasion and hedging patterns
2. **LLM dual-pass analysis** — two independent LLM evaluations of behavioral consistency
3. **Dynamic prompting** — adaptive probe generation based on detected failure modes

### Trust Grading
Multi-dimensional scoring system with temporal decay. Trust grades (A–E) reflect behavioral consistency across multiple interactions, not single-response quality. Scores decay over time — a model must maintain consistency to preserve its grade.

### Threat Monitor
Real-time detection of:
- Prompt injection attempts
- Model evasion patterns (topic deflection, false agreement, semantic substitution)
- Behavioral drift across conversation turns

### Verifiable Interaction Ledger (VIL)
Cryptographic audit trail for all model interactions:
- SHA-256 hash-chained entries — each interaction is linked to its predecessor
- Ed25519 digital signatures — entries are signed and tamper-evident
- Complete interaction history — every prompt, response, and PLI evaluation is recorded

The VIL ensures that behavioral audits are reproducible and that no interaction can be retroactively modified or deleted.

---

## Behavioral Metrics

| Metric | Description |
|--------|-------------|
| **CFR** (Consistency Failure Rate) | Proportion of interrogation cycles where the model contradicts a prior position |
| **RR** (Refusal Rate) | Proportion of probes where the model refuses to engage or deflects |
| **AD** (Assertion Density) | Rate of unsupported claims per response — high AD indicates false confidence |

---

## Testing

217 tests covering all modules. All LLM-dependent tests use a deterministic `EchoBackend` — no API keys required. The test suite verifies behavioral detection logic independently of any specific LLM provider, ensuring that AIntegrity's interrogation methodology is testable without external dependencies.

---

## Research Context

Two papers underpin the theoretical framework:

1. **"Epistemic Decay in Agentic AI Systems"** (Dark, 2026) — formalises the concept of epistemic decay as distinct from alignment failure, and proposes detection criteria based on behavioral consistency metrics.

2. **"Persistent Logical Interrogation: A Formal Methodology for Behavioural Consistency Auditing in Large Language Models"** (Dark, 2026c) — specifies the PLI protocol, its five-state cycle, nine failure modes, and the mathematical basis for trust grading with temporal decay.

---

## What This Project Demonstrates

- **Original theoretical contribution to AI safety** — epistemic decay as a distinct failure mode, not reducible to alignment or hallucination
- **Systematic behavioral auditing methodology** — PLI protocol with formal state machine and categorised failure modes
- **Cryptographic audit trail design** — hash-chained, signed interaction ledger ensuring reproducibility and tamper-evidence
- **Formal interrogation protocol design** — five-state cycle with escalation logic and forced resolution
